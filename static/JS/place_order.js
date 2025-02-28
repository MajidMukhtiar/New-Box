document.getElementById("orderForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission

    // Get user details
    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let address = document.getElementById("address").value;

    // Extract cart details
    let cartTable = document.getElementById("cartTable"); // Ensure the table has `id="cartTable"`
    let rows = cartTable.getElementsByTagName("tr");
    let cartItems = [];

    for (let i = 1; i < rows.length; i++) { // Start from 1 to skip headers
        let cells = rows[i].getElementsByTagName("td");
        let item = {
            name: cells[0].innerText,
            price: parseFloat(cells[1].innerText.replace("$", "")),
            quantity: parseInt(cells[2].innerText),
            subtotal: parseFloat(cells[3].innerText.replace("$", ""))
        };
        cartItems.push(item);
    }

    // Calculate total price
    let totalPrice = cartItems.reduce((sum, item) => sum + item.subtotal, 0);

    // Generate receipt HTML
    let receiptHTML = `
        <h2>Order Receipt</h2>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Address:</strong> ${address}</p>
        <h3>Items Ordered:</h3>
        <table border="1" width="100%">
            <tr><th>Car</th><th>Price</th><th>Quantity</th><th>Subtotal</th></tr>
            ${cartItems.map(item => `
                <tr>
                    <td>${item.name}</td>
                    <td>$${item.price}</td>
                    <td>${item.quantity}</td>
                    <td>$${item.subtotal}</td>
                </tr>
            `).join('')}
        </table>
        <h3>Total Amount: $${totalPrice.toFixed(2)}</h3>
    `;

    // Display receipt
    document.getElementById("receipt").innerHTML = receiptHTML;
    document.getElementById("receipt").style.display = "block";
    document.getElementById("printBtn").style.display = "inline-block";

    // Send data to server
    let formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("address", address);
    formData.append("cart", JSON.stringify(cartItems));
    formData.append("total_price", totalPrice);

    try {
        const response = await fetch("/submit_order", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        alert(data.message);

        if (response.ok) {
            window.location.href = "/";
        }
    } catch (error) {
        console.error("Error submitting order:", error);
        alert("Failed to submit order. Please try again.");
    }
});

// Print receipt function
function printReceipt() {
    let printContents = document.getElementById("receipt").innerHTML;
    let newWindow = window.open('', '', 'width=800,height=600');
    newWindow.document.write('<html><head><title>Print Receipt</title></head><body>');
    newWindow.document.write(printContents);
    newWindow.document.write('</body></html>');
    newWindow.document.close();
    newWindow.print();
}
