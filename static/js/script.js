document.addEventListener('DOMContentLoaded', function() {
    const menuContainer = document.getElementById('menu-container');

    // Improved error handling and user feedback
    function handleError(message) {
        console.error(message);
        menuContainer.innerHTML = message;
    }

    function addDishCalories(caloriesToAdd) {
        // Retrieve the current total from localStorage, or start at 0 if it doesn't exist yet
        let totalCalories = parseInt(localStorage.getItem('totalCalories') || '0');
        
        // Add the dish's calories to the total
        totalCalories += caloriesToAdd;
        
        // Store the new total back into localStorage
        localStorage.setItem('totalCalories', totalCalories.toString());
        
        // Update the total calories display
        document.getElementById('total-calories').textContent = `Total Calories: ${totalCalories}`;
    }
    

    // Fetch the list of dish names from the '/menu' endpoint
    fetch('/menu')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status}`);
            }
            return response.json();
        })
        .then(dishNames => {
            // Clear any existing items
            menuContainer.innerHTML = '';

            // Create a button for each dish name
            dishNames.forEach(dishName => {
                const button = document.createElement('button');
                button.textContent = dishName;
                button.classList.add('dish-button');
                button.addEventListener('click', function() {
                    // Redirect to the dish details page
                    window.location.href = `/menu/${encodeURIComponent(dishName)}`;
                });
                menuContainer.appendChild(button);
            });
        })
        .catch(error => handleError('Failed to load the menu. Please try again later.'));

    // Attach the calculateTotalCalories function to the Calculate Total Calories button
    const calculateBtn = document.getElementById('calculate-btn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', calculateTotalCalories);
    }
});
