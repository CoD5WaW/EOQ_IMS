# Django Economic Order Quantity (EOQ) Inventory Management System

A comprehensive inventory management system built with Django that integrates Economic Order Quantity (EOQ) modeling to optimize inventory management and purchasing decisions.

## Overview

This application helps businesses efficiently manage inventory by implementing EOQ principles to determine the optimal order quantity for products, minimizing total inventory costs including holding costs and ordering costs.

## Features

- **User Authentication & Management**: Secure login system with role-based access control
- **Dashboard**: Visual overview of key inventory metrics and alerts
- **Inventory Management**: 
  - Track stock levels, locations, and movements
  - Product categorization and details
  - Low stock alerts and notifications
- **Purchasing Module**: 
  - EOQ calculations for optimal order quantities
  - Purchase order creation and management
  - Supplier management
- **Warehouse Management**: 
  - Manage multiple locations and storage areas
  - Stock transfers between locations
  - Receiving and dispatch operations
- **Analytics**: 
  - Inventory performance metrics
  - Cost analysis and optimization insights
  - Demand forecasting
  - Custom reports generation

## Technology Stack

- **Backend**: Django 5.2
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5 with Crispy Forms
- **Additional Libraries**:
  - widget_tweaks
  - mathfilters (for EOQ calculations)
  - crispy_bootstrap5
  - Django Humanize

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- Git

### Setup Instructions

1. **Clone the repository**
   ```
   git clone https://github.com/CoD5WaW/EOQ_IMS.git
   cd EOQ_IMS
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Create a PostgreSQL database named `eoq_ims_db`
   - Update database settings in `settings.py` if needed

5. **Apply migrations**
   ```
   python manage.py migrate
   ```

6. **Create a superuser**
   ```
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```
   python manage.py runserver
   ```

8. Access the application at `http://127.0.0.1:8000/`

## Project Structure

```
eoq_ims_project/
├── analytics/            # Analytics and reporting
├── authentication/       # User authentication functionality
├── dashboard/            # Main dashboard views
├── eoq_ims_project/      # Project configuration
├── inventory/            # Inventory management functionality
├── purchasing/           # Purchasing and EOQ implementation
├── static/               # Static files (CSS, JS, images)
├── staticfiles/          # Collected static files
├── templates/            # HTML templates
├── user/                 # User profile management
├── warehouse/            # Warehouse operations
└── manage.py             # Django management script
```

## Usage

### EOQ Implementation

The EOQ formula calculates optimal order quantity using:

```
EOQ = sqrt((2 * Annual Demand * Order Cost) / Holding Cost)
```

Our implementation accounts for:
- Variable lead times
- Quantity discounts
- Demand fluctuations

### Key System Workflows

1. **Inventory Management**:
   - Add/edit products with relevant EOQ parameters
   - Track inventory levels and movements
   - Set reorder points based on EOQ calculations

2. **Purchasing Process**:
   - System identifies items requiring replenishment
   - EOQ model suggests optimal order quantities
   - Generate purchase orders with supplier selection

3. **Warehouse Operations**:
   - Receive and store incoming inventory
   - Process outgoing orders
   - Conduct inventory audits

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Link: [https://github.com/CoD5WaW/EOQ_IMS](https://github.com/CoD5WaW/EOQ_IMS)
