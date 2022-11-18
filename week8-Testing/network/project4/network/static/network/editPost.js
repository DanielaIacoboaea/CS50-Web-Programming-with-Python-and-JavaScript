document.addEventListener("DOMContentLoaded", function(){

    const editButton = document.querySelectorAll('.edit-btn');
    editButton.forEach(edit => {

        edit.addEventListener('click', () => {
            const saveBtn = edit.previousElementSibling;
            const editForm = edit.closest('[data-formId]');
            const editPostId = editForm.dataset.formid;
            const buildTextareaId = `t_${editPostId}`;
            const editContentTextarea = document.querySelector('#'+ buildTextareaId);
            const currentContent = editContentTextarea.previousElementSibling;
            edit.style.display = 'none';
            saveBtn.style.display = 'block';
            currentContent.style.display = 'none';
            editContentTextarea.style.display = 'block';

            editForm.onsubmit = () => {
                const formContent = new FormData(editForm);
                const formContentText = formContent.get('updateContent');
                const userProfileRequest = document.querySelector('#profile-id').innerHTML;
                const updatePostId = editPostId;

                const buildUrlFetch = `${parseInt(userProfileRequest)}`;
                const updatePostBody = {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        newContent: formContentText,
                        postId: parseInt(editPostId)
                    })
                }

                fetch(buildUrlFetch, updatePostBody)
                .then(response => {
                    if (response.status == 204){
                        currentContent.innerHTML = formContentText;
                        editContentTextarea.style.display = 'none';
                        currentContent.style.display = 'block';
                        saveBtn.style.display = 'none';
                        edit.style.display = 'block';
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