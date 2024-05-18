function query() {
    const query = document.getElementById('search-input').value

    fetch('http://127.0.0.1:2000/retrieve-relevant-documents', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(query)
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        console.log('Response from server:', data);
        clearForList()
        createList(data.relevant_documents)
    }).catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        // Handle errors
    });
}

function clearForList() {
    let imageContainer = document.getElementById("inactive-image-container");
    if (imageContainer) {
        imageContainer.remove();
    }

    let listContainerToDelete = document.getElementById("list-container");
    if (listContainerToDelete) {
        listContainerToDelete.remove();
    }

}


function createList(relevantDocuments) {
    let container = document.getElementById("container")

    const listContainer = document.createElement("div");
    listContainer.classList.add("list-container");
    listContainer.id = "list-container"


    for (const relevantDocument of relevantDocuments) {
        let listItem = document.createElement("div");
        listItem.classList.add("list-item");

        let link = document.createElement("a");
        link.href = relevantDocument[0]
        link.textContent = relevantDocument[0]
        link.target = "_blank"

        listItem.append(link)
        listContainer.appendChild(listItem)
    }

    container.appendChild(listContainer)
}