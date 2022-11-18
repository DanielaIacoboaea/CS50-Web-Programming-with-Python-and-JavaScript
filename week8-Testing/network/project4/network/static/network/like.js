document.addEventListener("DOMContentLoaded", function(){

    const likeButton = document.querySelectorAll('.like-button');
    likeButton.forEach(like => {

        like.addEventListener('click', () => {
        
        let likeAction;
        let postId = like.nextElementSibling.innerHTML;
       
        let likesCount = parseInt(like.innerHTML.split('>')[2]);

        if (like.classList.contains('like')){
            like.classList.remove('like');
            likeAction = 'unlike';
        }else{
            like.classList.add('like');
            likeAction = 'like';
        }

        const url = `likes/${parseInt(postId)}`;
        const likeBody = {
            method: 'POST', 
            body: JSON.stringify({
                like: likeAction
              }),
              headers: {
                'Content-Type': 'application/json'
              }
        };
        if (likeAction === 'like'){
            
            fetch(url, likeBody)
            .then(response => {
                if (response.status == 204){
                    like.innerHTML = `<span class=\"material-symbols-outlined\" style=\"font-variation-settings: \'FILL\' 1, \'wght\' 700, \'GRAD\' 0, \'opsz\' 48;\">favorite</span>${likesCount + 1}</p>`;
                }
            })
            .then(result => console.log(result))
            .catch(error => {
                console.log("error: ", error);
            })
        }else {

            fetch(url, likeBody)
            .then(response => {
                if (response.status == 204){
                    like.innerHTML = `<span class=\"material-symbols-outlined\">favorite</span>${likesCount - 1}</p>`;
                }
            })
            .then(result => console.log(result))
            .catch(error => {
                console.log("error: ", error);
            })
        }
    });
    });
})