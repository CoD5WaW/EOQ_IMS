/**
 * FormsetHandler - Manages Django formsets with dynamic add/remove
 */
document.addEventListener('DOMContentLoaded', function() {
    const FormsetHandler = {
        init: function(options) {
            this.formsetPrefix = options.prefix || 'form';
            this.addButtonSelector = options.addButtonSelector || '.add-form';
            this.removeButtonSelector = options.removeButtonSelector || '.remove-form';
            this.formSelector = options.formSelector || '.dynamic-form';
            this.totalFormsSelector = `#id_${this.formsetPrefix}-TOTAL_FORMS`;
            
            this.bindEvents();
            this.updateFormIndexes();
        },
        
        bindEvents: function() {
            const self = this;
            
            // Add form event
            document.querySelectorAll(this.addButtonSelector).forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.addForm();
                });
            });
            
            // Remove form event - using event delegation for dynamic elements
            document.addEventListener('click', function(e) {
                if (e.target && e.target.matches(self.removeButtonSelector)) {
                    e.preventDefault();
                    self.removeForm(e.target);
                }
            });
        },
        
        addForm: function() {
            // Get the form template
            const formCount = document.querySelector(this.totalFormsSelector).value;
            const template = document.querySelector(`${this.formSelector}:last-child`);
            const newForm = template.cloneNode(true);
            
            // Update form ID and name attributes
            const regex = new RegExp(`${this.formsetPrefix}-\\d+`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(regex, `${this.formsetPrefix}-${formCount}`);
            
            // Clear form values
            newForm.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.type === 'checkbox') {
                    input.checked = false;
                } else if (input.type !== 'hidden') {
                    input.value = '';
                }
            });
            
            // Insert the new form
            template.parentNode.insertBefore(newForm, null);
            
            // Update the total form count
            document.querySelector(this.totalFormsSelector).value = parseInt(formCount) + 1;
            
            // Update all form indexes
            this.updateFormIndexes();
        },
        
        removeForm: function(button) {
            const formCount = document.querySelector(this.totalFormsSelector).value;
            
            if (parseInt(formCount) > 1) {
                const formToRemove = button.closest(this.formSelector);
                formToRemove.remove();
                
                // Update the total form count
                document.querySelector(this.totalFormsSelector).value = parseInt(formCount) - 1;
                
                // Update all form indexes
                this.updateFormIndexes();
            } else {
                alert('You cannot remove all forms. At least one form is required.');
            }
        },
        
        updateFormIndexes: function() {
            const forms = document.querySelectorAll(this.formSelector);
            const totalForms = forms.length;
            
            document.querySelector(this.totalFormsSelector).value = totalForms;
            
            forms.forEach((form, index) => {
                // Update form index (for visual display)
                const indexElement = form.querySelector('.form-index');
                if (indexElement) {
                    indexElement.textContent = index + 1;
                }
            });
        }
    };
    
    // Initialize for purchase order items
    if (document.querySelector('#id_items-TOTAL_FORMS')) {
        FormsetHandler.init({
            prefix: 'items',
            addButtonSelector: '.add-item',
            removeButtonSelector: '.remove-item',
            formSelector: '.item-form'
        });
    }
});