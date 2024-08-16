document.getElementById('search').addEventListener('input', function() {
    let query = this.value;
    if (query.length > 0) {
        fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const suggestionsContainer = document.getElementById('suggestions');
                suggestionsContainer.classList.add("p-4", "rounded-xl", "border" ,"shadow","mt-2")
                suggestionsContainer.innerHTML = '';
                if (data.length > 0) {
                    suggestionsContainer.style.display = 'block';
                    data.forEach(term => {
                        let item = document.createElement('div');
                        item.classList.add('suggestion-item','cursor-pointer',"p-2");
                        item.onclick = function() {
                            window.location.href = "/search?q="+term;
                            //document.getElementById('search').value = term;
                            suggestionsContainer.style.display = 'none';
                        };
                        item.innerHTML ='<i class="fa-solid fa-magnifying-glass mr-2"></i>'+term;
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
document.addEventListener('click', function(event) {
    const suggestionsContainer = document.getElementById('suggestions');
    if (!suggestionsContainer.contains(event.target) && event.target.id !== 'search') {
        suggestionsContainer.style.display = 'none';
    }
});
