document.getElementById("orderForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    // Get user details
    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let address = document.getElementById("address").value;

    if (!name || !email || !address) {
        alert("Please fill all fields.");
        return;
    }

    // Send order data to backend but do NOT clear cart yet
    let orderData = { name, email, address };

    try {
        const response = await fetch("/submit_order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(orderData)
        });

        const data = await response.json();

        if (response.ok) {
            displayReceipt(data.receipt); // Show receipt first
        } else {
            alert(data.error || "Order failed.");
        }
    } catch (error) {
        console.error("Error submitting order:", error);
        alert("Failed to submit order. Please try again.");
    }
});

// Function to Display Receipt on Webpage
function displayReceipt(receipt) {
    let receiptHTML = `
        <h2>Order Receipt</h2>
        <p><strong>Name:</strong> ${receipt.name}</p>
        <p><strong>Email:</strong> ${receipt.email}</p>
        <p><strong>Address:</strong> ${receipt.address}</p>
        <h3>Items Ordered:</h3>
        <table border="1" width="100%">
            <tr><th>Car</th><th>Price</th><th>Quantity</th><th>Subtotal</th></tr>
            ${receipt.cart_items.map(item => `
                <tr>
                    <td>${item.car_name}</td>
                    <td>$${item.price}</td>
                    <td>${item.quantity}</td>
                    <td>$${item.subtotal}</td>
                </tr>
            `).join('')}
        </table>
        <h3>Total Amount: $${receipt.total_price.toFixed(2)}</h3>
    `;

    document.getElementById("receipt").innerHTML = receiptHTML;
    document.getElementById("receipt").style.display = "block";
    document.getElementById("printBtn").style.display = "inline-block";
}

// Print & THEN Clear Cart
document.getElementById("printBtn").addEventListener("click", function () {
    let printContents = document.getElementById("receipt").innerHTML;
    let newWindow = window.open('', '', 'width=800,height=600');
    newWindow.document.write('<html><head><title>Print Receipt</title></head><body>');
    newWindow.document.write(printContents);
    newWindow.document.write('</body></html>');
    newWindow.document.close();
    newWindow.print();

    // Now clear the cart AFTER printing
    fetch("/clear_cart", { method: "POST" })
        .then(() => {
            alert("Cart Cleared!");
            window.location.href = "/"; // Redirect to home
        })
        .catch(err => console.error("Cart Clear Error:", err));
});
