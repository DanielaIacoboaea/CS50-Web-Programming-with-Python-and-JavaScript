document.addEventListener('DOMContentLoaded', function(){

    const commentBtns = document.querySelectorAll('.comment-btn');

    commentBtns.forEach(commentBtn => {

        commentBtn.addEventListener('click', () => {
            const postCard = commentBtn.closest('[data-postid]');
            const formComment = postCard.lastElementChild.lastElementChild;
            const postId = postCard.dataset.postid;
            const postOwner = postCard.dataset.postOwner;

            formComment.style.display = 'block';

            formComment.addEventListener.onsubmit = () => {
                
                const commentContent = document.querySelector('#addComment').value;
                let postFormId = formComment.dataset.formPost;

                let sendFormComment = new FormData(formComment);

                const addCommentBody = {
                    method: 'post',
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                    body: sendFormComment
                };
                
                fetch("comments", addCommentBody)
                .then(response => {
                    if (response.status == 204){
                        const commentCard = formComment.closest('[data-comment-post-id]');
                        const newComment = document.createElement('p');
                        const userName = formComment.dataset.username;
                        newComment.innerHTML = `<strong style=\"color: #1DA1F2;\">${userName}</strong>: ${commentContent}`;
                        if (commentCard != null){
                            commentCard.append(newComment);
                            formComment.style.display = 'none';
                            formComment.firstElementChild.lastElementChild.style.display = 'none';
                        }else{
                            formComment.firstElementChild.lastElementChild.style.display = 'none';
                            formComment.firstElementChild.style.display = 'none';
                            formComment.append(newComment);
                        }
                    }
                })
                .catch(error => {
                    console.log("error: ", error);
                })
                return false;
            };
        });
    });
})

