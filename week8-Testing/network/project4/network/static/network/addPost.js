document.addEventListener("DOMContentLoaded", function(){

    document.querySelector('#add-post').onsubmit = () => {

        const form = document.querySelector('#add-post');
        let sendForm = new FormData(form);
        const image = document.querySelector('#id_image');
        const imageName = document.querySelector('#id_image').value;
        const content = document.querySelector('#id_content').value;
        
        sendForm.append("image", image.files[0]);
        sendForm.append("name", "create-post");

        const postBody = {
            method: 'POST', 
            'Content-Type': 'multipart/form-data',
            body: sendForm
        };
        fetch("", postBody)
        .then(response => {
            if (response.status == 204){
                const posts = document.querySelector('#posts-wrapper');
                const username = document.querySelector('#add-post').previousElementSibling.innerHTML;

                let createCard = document.createElement('div');
                createCard.classList.add('card');

                let addCardBodyElement = document.createElement('div');
                addCardBodyElement.classList.add('card-body');

                let addCardUsername = document.createElement('h5');
                addCardUsername.classList.add('card-title');
                addCardUsername.innerHTML = `<strong>${username}</strong>`;
                addCardBodyElement.append(addCardUsername);

                let addCartContent = document.createElement('p');
                addCartContent.classList.add('card-text');
                addCartContent.innerHTML = content;
                addCardBodyElement.append(addCartContent);

                if (image.files.length != 0){
                    let addCartImage = document.createElement('img');
                    let filename = image.files[0].name
                    addCartImage.src= `/images/images/${filename}`;
                    addCardBodyElement.append(addCartImage);
                }

                createCard.append(addCardBodyElement);

                let addCardFooter = document.createElement('div');
                addCardFooter.classList.add('card-footer', 'text-muted');

                let addCardBubble = document.createElement('div');
                addCardBubble.classList.add('card-bubble');

                let addCommentBtn = document.createElement('p');
                addCommentBtn.classList.add('comment-btn');
                addCommentBtn.innerHTML = `<span class=\"material-symbols-outlined\">chat_bubble</span>0`;
                addCardBubble.append(addCommentBtn);

                let addLikeBtn = document.createElement('p');
                addLikeBtn.classList.add('like-button');
                addLikeBtn.innerHTML = `<span class=\"material-symbols-outlined\">favorite</span>0`;
                addCardBubble.append(addLikeBtn);

                let addEditBtn = document.createElement('p');
                addEditBtn.innerHTML = `<a class=\"edit-btn submit-btn\" href=\"#\">Edit</a>`;
                addCardBubble.append(addEditBtn);

                addCardFooter.append(addCardBubble);
                createCard.append(addCardFooter);
                form.firstElementChild.firstElementChild.value = "What\'s happening?";
                image.value = '';
                document.querySelector('#id_content').value ='';
                posts.prepend(createCard);
            }
        })
        .catch(error => {
            console.log("error: ", error);
        })
        return false;
    };
})