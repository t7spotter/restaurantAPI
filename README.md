# RestaurantAPI 
Welcome to RestaurantAPI project, a Django and DRF project designed to streamline restaurant operations through a comprehensive API. This project offers a robust solution for managing menu items, processing orders, and organizing user groups within a restaurant ecosystem.

## Project Structure

In RestaurantAPI, we embrace a structured approach to user management, catering to the diverse roles and responsibilities within a restaurant setting. Our project revolves around three primary user groups, each tailored to fulfill specific functions:

1. **Manager**: Managers oversee the day-to-day operations, including menu management, order tracking, and staff status.
   
2. **Delivery Crew**: The delivery crew is responsible for order delivery logistics, ensuring timely and efficient distribution of orders to customers.

3. **Customer**: Customers interact with the system to browse the menu, place orders, and track their order status.

Each user group is equipped with tailored permissions and privileges to ensure smooth operations and maintain security standards throughout the platform.

Furthermore, new users who register on the platform are automatically assigned the customer role through a signal. This simplifies the onboarding process, ensuring that all new users have access to basic functionalities upon registration.

## Getting Started

To start using RestaurantAPI, follow these simple steps:

1. **Clone the Repository**: Use the following command to clone the repository to your local machine:

```bash
git clone https://github.com/t7spotter/restaurantAPI.git
```
Navigate to restaurantAPI folder:
```bash
cd restaurantAPI
```

And run the project, you can use Docker with docker-compose up to create new container with this app.

```bash
docker-compose up --build
```

## API Endpoints

### Menu Items

#### Get All Menu Items
```
GET /api/menu-items
```

#### Get a Specific Menu Item
```
GET /api/menu-items/<menu_item_id>
```

#### Create a New Menu Item (only manager user can use this method)
```
POST /api/menu-items
```
Example request body:
```json
{
  "title": "New Item",
  "price": 9.99,
  "featured": true,
  "category": "Category ID"
}
```

#### Update a Menu Item (only manager user can use this method)
```
PUT /api/menu-items/<menu_item_id>
```
Example request body:
```json
{
  "title": "Updated Item",
  "price": 12.99,
  "featured": false,
  "category": "New Category ID"
}
```

#### Delete a Menu Item (only manager user can use this method)
```
DELETE /api/menu-items/<menu_item_id>
```

### Categories

#### Get All Categories
```
GET /api/category
```

#### Get a Specific Category
```
GET /api/category/<category_id>
```

#### Create a New Category (only manager user can use this method)
```
POST /api/category
```
Example request body:
```json
{
  "slug": "new-category",
  "title": "New Category"
}
```

#### Update a Category (only manager user can use this method)
```
PUT /api/category/<category_id>
```
Example request body:
```json
{
  "slug": "updated-category",
  "title": "Updated Category"
}
```

#### Delete a Category (only manager user can use this method)
```
DELETE /api/category/<category_id>
```

### User Groups

#### Add a User to Manager Group (only manager user can use this method)
```
POST /api/groups/manager/users
```
Example request body:
```json
{
  "username": "username"
}
```

#### Remove a User from Manager Group (only manager user can use this method)
```
DELETE /api/groups/manager/users/<user_id>
```

#### Add a User to Delivery Crew Group (only manager user can use this method)
```
POST /api/groups/delivery-crew/users
```
Example request body:
```json
{
  "username": "username"
}
```

#### Remove a User from Delivery Crew Group (only manager user can use this method)
```
DELETE /api/groups/delivery-crew/users/<user_id>
```

### Cart

#### Get Cart Items
```
GET /api/cart/menu-items
```

#### Add Item to Cart
```
POST /api/cart/menu-items
```
Example request body:
```json
{
  "menuitem": "menu_item_id",
  "quantity": 2
}
```

#### Delete All Items from Cart
```
DELETE /api/cart/menu-items
```

### Orders

#### Get All Orders
```
GET /api/orders
```

#### Get a Specific Order
```
GET /api/orders/<order_id>
```

#### Create an Order
```
POST /api/orders
```

#### Update Delivery Status of an Order (only delivery crew user can use this method)
```
POST /api/delivery/<order_id>
```

### Delivery Crew

#### Get Orders Assigned to Delivery Crew (each delivery crew user only can check orders which assigned to them not for another delivery crew users) 
```
GET /api/delivery
```

#### Update Delivery Status of an Order by Delivery Crew (each delivery crew user only can change the status "delivered" orders which assigned to them not for another delivery crew users) 
```
POST /api/delivery/<order_id>
```

### Manager Actions

#### Get Undelivered Orders
```
GET /api/undelivered
```

#### Assign Order to a Delivery Crew
```
POST /api/undelivered/<order_id>
```

#### Get Delivered Orders
```
GET /api/delivered
```
Replace `<menu_item_id>`, `<category_id>`, `<user_id>`, and `<order_id>` with actual IDs when making requests.

### User Registration
New users can register by making a POST request to the following endpoint:
```bash
POST /auth/users/
```
The request body should include two required fields:
```json
{
    "username": "username",
    "password": "password"
}
```
new users who register on the platform are automatically assigned the 'customer' role through a signal. This simplifies the onboarding process, ensuring that all new users have access to basic functionalities upon registration.

## Sale Report API

This API provides endpoints to retrieve sale reports based on specific dates.

### Endpoints


#### GET /sale

Returns the sales report for today and amount of orders.

- Response:
```json
{
    "message": "Today (2024-05-01 13:35:02) sale is 137 for 7 orders."
}
```

#### POST /sale

- Body:
```json
{
  "start_date": "2023-4-27",
  "end_date": "2024-05-01"
}

```
** If you omit the `end_date`, the API calculates the sales from the `start_date` to today.

** If you omit both the `end_date` and `start_date`, the API calculates the sales for today only.~~~~

- Response:
```json
{
    "message": "Your sale from 2023-4-27 to 2024-05-01 is 2438 for 73 orders."
}
```
## Rating API
This API provides access for users to rate an item if they have ordered that item at least once.

### Endpoints
#### GET /rate
It Shows Menu items with rates counts and rates averages.
```json
[
    {
        "id": 1,
        "title": "Vanilla",
        "category": 5,
        "_category_title": "Ice creams",
        "price": "3.00",
        "featured": true,
        "rate": {
            "rate_count": 246,
            "rate_average": 8.9
        }
    },
    {
        "id": 2,
        "title": "Chocolate",
        "category": 5,
        "_category_title": "Ice creams",
        "price": "4.00",
        "featured": false,
        "rate": {
            "rate_count": 325,
            "rate_average": 8.74
        }
    },
    {
        "id": 3,
        "title": "Mango",
        "category": 5,
        "_category_title": "Ice creams",
        "price": "7.00",
        "featured": true,
        "rate": {
            "rate_count": 436,
            "rate_average": 9.14
        }
    },
  .
  .
  .
]
```
#### POST /rate/<<int:menuItem_id>>
Customers can submit a rating between 1 and 10 (just integer) in JSON format:
```json
{
  "rate": 9
}
```

## Users Address Management
users can get, add and remove their own addresses from profile
### Endpoints
GET /address

POST /address

DELETE /address/<<int:address_id>>

## And much more capabilities!


## Contributing

Feel free to contribute to this project by submitting pull requests or reporting issues.


