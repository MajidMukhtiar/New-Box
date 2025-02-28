document.addEventListener("DOMContentLoaded", async function() {
    try {
        const response = await fetch("/get_cars");
        const data = await response.json();

        if (!data.cars || !Array.isArray(data.cars)) {
            throw new Error("Invalid car data format.");
        }

        const carsContainer = document.getElementById("carsContainer"); 
        carsContainer.innerHTML = ""; 

        data.cars.forEach(car => {
            const carCard = document.createElement("div");
            carCard.classList.add("car-card");

            // Ensure the ID is passed as a string to avoid errors
            const carId = `'${car.id}'`;

            carCard.innerHTML = `
                <img src="${car.image_url}" alt="${car.name}" class="car-image">
                <h3>${car.name}</h3>
                <p>Price: $${car.price.toLocaleString()}</p>
                <p>${car.description}</p>
                <button onclick="addToCart(${carId})">Add to Cart</button>
            `;

            carsContainer.appendChild(carCard);
        });

    } catch (error) {
        console.error("Error fetching cars:", error);
    }
});

async function addToCart(carId) {
    try {
        const response = await fetch("/add_to_cart", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ car_id: carId }) // Send data as JSON
        });

        const data = await response.json();
        alert(data.message);
    } catch (error) {
        console.error("Error adding to cart:", error);
    }
}



// document.addEventListener("DOMContentLoaded", async function() {
//     try {
//         const response = await fetch("/get_cars");
//         const data = await response.json();

//         if (!data.cars || !Array.isArray(data.cars)) {
//             throw new Error("Invalid car data format.");
//         }

//         const carsContainer = document.getElementById("carsContainer"); 
//         carsContainer.innerHTML = ""; 

//         data.cars.forEach(car => {
          
            
//             const carCard = document.createElement("div");
//             carCard.classList.add("car-card");
// console.log(car);
//             carCard.innerHTML = `
//                 <img src="${car.image_url}" alt="${car.name}" class="car-image">
//                 <h3>${car.name}</h3>
//                 <p>Price: $${car.price.toLocaleString()}</p>
//                 <p>${car.description}</p>
//                 <button onclick="addToCart(${car.id})">Add to Cart</button>
              
//             `;

//             carsContainer.appendChild(carCard);
//             console.log(car.image_url);
//         });

//     } catch (error) {
//         console.error("Error fetching cars:", error);
//     }
// });


// async function addToCart(carId) {
//     const response = await fetch(`/add_to_cart/${carId}`, { method: "POST" });
//     const data = await response.json();
//     alert(data.message);
// }

// // Fetch cars when the page loads
// fetchCars();

