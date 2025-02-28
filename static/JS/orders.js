document.addEventListener("DOMContentLoaded", function () {
    fetchOrders();
    fetchTotalSales();  // Now correctly updates total sales
    fetchTotalOrders(); // Now correctly updates total orders
    fetchTopOrders();
});

async function fetchOrders() {
    try {
        const response = await fetch('/get_orders');
        const data = await response.json();

        const ordersTable = document.getElementById('orders-body');
        ordersTable.innerHTML = ""; // Clear previous entries

        if (data.orders.length === 0) {
            ordersTable.innerHTML = "<tr><td colspan='5' class='text-center'>No orders found.</td></tr>";
            return;
        }

        data.orders.forEach(order => {
            ordersTable.innerHTML += `
                <tr>
                    <td>${order._id}</td>
                    <td>${order.name}</td>
                    <td>${order.email}</td>
                    <td>${order.address}</td>
                    <td>$${order.total_price.toFixed(2)}</td>
                </tr>`;
        });
    } catch (error) {
        console.error("Error fetching orders:", error);
        const ordersTable = document.getElementById('orders-body');
        ordersTable.innerHTML = "<tr><td colspan='5' class='text-center'>Failed to load orders.</td></tr>";
    }
}

async function fetchTotalSales() {
    try {
        const response = await fetch("/total_sales");
        const data = await response.json();
        document.getElementById("total-sales").textContent = `$${parseFloat(data.total_sales).toFixed(2)}`;
    } catch (error) {
        console.error("Error fetching total sales:", error);
    }
}

async function fetchTotalOrders() {
    try {
        const response = await fetch("/total_orders");
        const data = await response.json();
        // Update the total orders in the correct element
        document.getElementById("total-orders").textContent = data.total_orders;
    } catch (error) {
        console.error("Error fetching total orders:", error);
    }
}

async function fetchTopOrders() {
    try {
        const response = await fetch("/top_orders");
        const data = await response.json();

        const topOrdersTable = document.getElementById('top-orders-body');
        topOrdersTable.innerHTML = ""; // Clear previous entries

        if (data.top_orders.length === 0) {
            topOrdersTable.innerHTML = "<tr><td colspan='5' class='text-center'>No top orders found.</td></tr>";
            return;
        }

        data.top_orders.forEach(order => {
            topOrdersTable.innerHTML += `
                <tr>
                    <td>${order._id}</td>  <!-- Accessing the MongoDB ObjectId (as string) -->
                    <td>${order.name}</td>
                    <td>${order.email}</td>
                    <td>${order.address}</td>
                    <td>$${order.total_price.toFixed(2)}</td>
                </tr>`;
        });
    } catch (error) {
        console.error("Error fetching top orders:", error);
    }
}


