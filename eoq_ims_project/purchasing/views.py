# purchasing/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.utils import timezone

from .models import Supplier, PurchaseOrder, POItem
from inventory.models import Product, InventoryTransaction, Inventory
from warehouse.models import Warehouse
from .forms import SupplierForm, PurchaseOrderForm, POItemForm, POItemFormSet


# Supplier Views
class SupplierListView(ListView):
    model = Supplier
    template_name = 'purchasing/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(supplier_name__icontains=search_query)
        return queryset


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'purchasing/supplier_detail.html'
    context_object_name = 'supplier'
    pk_url_kwarg = 'supplier_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_orders'] = PurchaseOrder.objects.filter(supplier=self.object).order_by('-order_date')
        return context


class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchasing/supplier_form.html'
    success_url = reverse_lazy('purchasing:supplier_list')

    def form_valid(self, form):
        messages.success(self.request, 'Supplier created successfully.')
        return super().form_valid(form)


class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchasing/supplier_form.html'
    pk_url_kwarg = 'supplier_id'

    def get_success_url(self):
        return reverse('purchasing:supplier_detail', kwargs={'supplier_id': self.object.supplier_id})

    def form_valid(self, form):
        messages.success(self.request, 'Supplier updated successfully.')
        return super().form_valid(form)


class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'purchasing/supplier_confirm_delete.html'
    success_url = reverse_lazy('purchasing:supplier_list')
    pk_url_kwarg = 'supplier_id'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Supplier deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Purchase Order Views
class PurchaseOrderListView(ListView):
    model = PurchaseOrder
    template_name = 'purchasing/po_list.html'
    context_object_name = 'purchase_orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(po_status=status_filter)
        return queryset.order_by('-order_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PurchaseOrder.STATUS_CHOICES
        return context


class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    template_name = 'purchasing/po_detail.html'
    context_object_name = 'po'
    pk_url_kwarg = 'po_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['status_choices'] = PurchaseOrder.STATUS_CHOICES
        return context


class PurchaseOrderCreateView(CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchasing/po_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = POItemFormSet(self.request.POST, instance=self.object)
        else:
            POItemInlineFormSet = inlineformset_factory(
                PurchaseOrder, POItem, form=POItemForm, formset=POItemFormSet,
                extra=1, can_delete=True
            )
            data['items'] = POItemInlineFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
        
        messages.success(self.request, 'Purchase Order created successfully.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('purchasing:po_detail', kwargs={'po_id': self.object.po_id})


class PurchaseOrderUpdateView(UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchasing/po_form.html'
    pk_url_kwarg = 'po_id'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = POItemFormSet(self.request.POST, instance=self.object)
        else:
            POItemInlineFormSet = inlineformset_factory(
                PurchaseOrder, POItem, form=POItemForm, formset=POItemFormSet,
                extra=1, can_delete=True
            )
            data['items'] = POItemInlineFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
        
        messages.success(self.request, 'Purchase Order updated successfully.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('purchasing:po_detail', kwargs={'po_id': self.object.po_id})


class PurchaseOrderDeleteView(DeleteView):
    model = PurchaseOrder
    template_name = 'purchasing/po_confirm_delete.html'
    success_url = reverse_lazy('purchasing:po_list')
    pk_url_kwarg = 'po_id'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Purchase Order deleted successfully.')
        return super().delete(request, *args, **kwargs)


def update_po_status(request, po_id):
    """Update the status of a Purchase Order"""
    po = get_object_or_404(PurchaseOrder, pk=po_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(PurchaseOrder.STATUS_CHOICES):
            old_status = po.po_status
            po.po_status = new_status
            
            # If status changed to 'received', create inventory transactions
            if new_status == 'received' and old_status != 'received':
                po.actual_delivery = timezone.now()
                
                # Get first warehouse (this could be improved by allowing selection)
                warehouse = Warehouse.objects.filter(active=True).first()
                if warehouse:
                    for item in po.items.all():
                        # Create inventory transaction for receipt
                        InventoryTransaction.objects.create(
                            product=item.product,
                            warehouse=warehouse,
                            transaction_type='receipt',
                            quantity=item.quantity,
                            reference_document='PO',
                            reference_id=po.po_id,
                            notes=f"Receipt from PO #{po.po_id}"
                        )
                        # The update_inventory method will be called automatically thanks to our model
                else:
                    messages.error(request, 'Cannot process receipt: No active warehouse found.')
                    return redirect('purchasing:po_detail', po_id=po_id)
            
            po.save()
            messages.success(request, f'Purchase Order status updated to {dict(PurchaseOrder.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status value.')
    
    return redirect('purchasing:po_detail', po_id=po_id)