const mobileSearch = document.getElementById('searchMobile')
const searchField = document.getElementById('search')


searchField.addEventListener('input', function () {


    let query = this.value;
    if (query.length > 0) {
        fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const suggestionsContainer = document.getElementById('suggestions');
                suggestionsContainer.classList.add("p-4", "rounded-xl", "border", "shadow", "mt-2")
                suggestionsContainer.innerHTML = '';
                if (data.length > 0) {
                    suggestionsContainer.style.display = 'block';
                    data.forEach(term => {
                        let item = document.createElement('div');
                        item.classList.add('suggestion-item', 'cursor-pointer', "p-2");
                        item.onclick = function () {
                            window.location.href = "/search?q=" + term;
                            //document.getElementById('search').value = term;
                            suggestionsContainer.style.display = 'none';
                        };
                        item.innerHTML = (term.length > 60)?'<i class="fa-solid fa-magnifying-glass mr-2"></i>' + term.slice(0,60)+"...":'<i class="fa-solid fa-magnifying-glass mr-2"></i>'+term;
                        suggestionsContainer.appendChild(item);
                    });
                } else {
                    suggestionsContainer.style.display = 'none';
                }
            });
    } else {
        document.getElementById('suggestions').style.display = 'none';
    }
});

// Hide suggestions when clicking outside
document.addEventListener('click', function (event) {
    const suggestionsContainer = document.getElementById('suggestions');
    if (!suggestionsContainer.contains(event.target) && event.target.id !== 'search') {
        suggestionsContainer.style.display = 'none';
    }
});


/*
var searchField  = document.getElementById("search")
var clearBtn  = document.getElementById("clearBtn")

clearBtn.addEventListener('click',()=>{
    searchField.r
})

*/


function validateImageUrls() {
    // Loop through each image element with the 'data-url' attribute
    document.querySelectorAll('img[data-url]').forEach(function (img) {

        const imageUrl = img.getAttribute('data-url');
        const mode = img.getAttribute('data-src');
        // Create a new Image object to check if the URL is valid
        var tempImage = new Image();
        tempImage.onload = function () {
            img.src = imageUrl;  // Set the src if the image loads successfully
        };
        tempImage.onerror = function () {
            if (mode == "fav") {
                img.src = '/static/default-favicon.png'  // Remove the image element if the URL is invalid
            }
            else {
                img.remove()
            }
        };
        tempImage.src = imageUrl;  // Set the src to trigger the load/error events
    });
}

window.onload = validateImageUrls;



