TRUNCATE order_items, orders, products, customers RESTART IDENTITY CASCADE;

INSERT INTO customers (name, email, city)
VALUES
('Rahul Sharma', 'rahul@example.com', 'Ahmedabad'),
('Priya Patel', 'priya@example.com', 'Mumbai'),
('Amit Joshi', 'amit@example.com', 'Delhi'),
('Siddharth Shah', 'siddharth@example.com', 'Ahmedabad'),
('Ananya Rao', 'ananya@example.com', 'Bangalore'),
('Vikram Malhotra', 'vikram@example.com', 'Mumbai'),
('Neha Gupta', 'neha@example.com', 'Delhi');

INSERT INTO products (name, category, price)
VALUES
('MacBook Pro', 'Laptop', 150000.00),
('iPhone 15', 'Mobile', 85000.00),
('Sony Headphones', 'Accessories', 12000.00),
('iPad Air', 'Tablet', 60000.00),
('Dell Monitor', 'Accessories', 25000.00),
('Logitech Mouse', 'Accessories', 3000.00);

INSERT INTO orders (customer_id, total_amount, status)
VALUES
(1, 162000.00, 'completed'),  
(2, 85000.00, 'completed'),   
(3, 12000.00, 'pending'),     
(4, 60000.00, 'completed'),   
(5, 178000.00, 'completed'),  
(2, 15000.00, 'cancelled'),   
(6, 85000.00, 'completed'),  
(1, 3000.00, 'completed');   

INSERT INTO order_items (order_id, product_id, quantity)
VALUES
(1, 1, 1), (1, 3, 1),        
(2, 2, 1),                    
(3, 3, 1),                   
(4, 4, 1),                  
(5, 1, 1), (5, 5, 1), (5, 6, 1),
(6, 5, 1),                   
(7, 2, 1),                   
(8, 6, 1);                  
