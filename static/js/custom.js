(function() {
	'use strict';

	var tinyslider = function() {
		var el = document.querySelectorAll('.testimonial-slider');

		if (el.length > 0) {
			var slider = tns({
				container: '.testimonial-slider',
				items: 1,
				axis: "horizontal",
				controlsContainer: "#testimonial-nav",
				swipeAngle: false,
				speed: 700,
				nav: true,
				controls: true,
				autoplay: true,
				autoplayHoverPause: true,
				autoplayTimeout: 3500,
				autoplayButtonOutput: false
			});
		}
	};
	tinyslider();

	


	// var sitePlusMinus = function() {

	// 	var value,
  //   		quantity = document.getElementsByClassName('quantity-container');

	// 	function createBindings(quantityContainer) {
	//       var quantityAmount = quantityContainer.getElementsByClassName('quantity-amount')[0];
	//       var increase = quantityContainer.getElementsByClassName('increase')[0];
	//       var decrease = quantityContainer.getElementsByClassName('decrease')[0];
	//       increase.addEventListener('click', function (e) { increaseValue(e, quantityAmount); });
	//       decrease.addEventListener('click', function (e) { decreaseValue(e, quantityAmount); });
	//     }

	//     function init() {
	//         for (var i = 0; i < quantity.length; i++ ) {
	// 					createBindings(quantity[i]);
	//         }
	//     };

	//     function increaseValue(event, quantityAmount) {
	//         value = parseInt(quantityAmount.value, 10);

	//         console.log(quantityAmount, quantityAmount.value);

	//         value = isNaN(value) ? 0 : value;
	//         value++;
	//         quantityAmount.value = value;
	//     }

	//     function decreaseValue(event, quantityAmount) {
	//         value = parseInt(quantityAmount.value, 10);

	//         value = isNaN(value) ? 0 : value;
	//         if (value > 0) value--;

	//         quantityAmount.value = value;
	//     }
	    
	//     init();
		
	// };
	// sitePlusMinus();


})()

document.addEventListener("DOMContentLoaded", function(){
	// Sélectionne tous les boutons d'ajout au panier
	const addButtons = document.querySelectorAll(".btn-add-to-cart");

	addButtons.forEach(function(button) {
			button.addEventListener("click", function(e) {
					e.preventDefault();
					// Récupérer l'ID du produit depuis l'attribut data
					let productId = button.getAttribute("data-product-id");

					fetch("{% url 'add_to_cart' %}", {
							method: "POST",
							headers: {
									"Content-Type": "application/json",
									"X-CSRFToken": getCookie("csrftoken")  // Fonction pour récupérer le token CSRF
							},
							body: JSON.stringify({ product_id: productId })
					})
					.then(response => response.json())
					.then(data => {
							if(data.error) {
									alert(data.error);
							} else {
									alert(data.message);
									// Optionnel : mettre à jour l’affichage du total du panier
									// document.querySelector("#cart-count").innerText = data.total;
							}
					})
					.catch(error => console.error("Erreur:", error));
			});
	});
});

/* Exemple de fonction pour récupérer le CSRF token depuis les cookies */
function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== "") {
			const cookies = document.cookie.split(";");
			for (let i = 0; i < cookies.length; i++) {
					const cookie = cookies[i].trim();
					// Le cookie commence avec le nom ?
					if (cookie.substring(0, name.length + 1) === (name + "=")) {
							cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
							break;
					}
			}
	}
	return cookieValue;
}
