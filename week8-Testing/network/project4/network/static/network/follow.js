
document.addEventListener("DOMContentLoaded", function(){

    const followBtn = document.querySelector('#follow-btn');
    const unfollowBtn = document.querySelector('#unfollow-btn');
    const userProfile = document.querySelector('#profile-id').innerHTML;
    const followersCount = document.querySelector('#followers-count');
    let updateFollowersCount;

    followBtn.addEventListener('click', () => {

        const urlProfile = `${parseInt(userProfile)}`;
        const fetchBody = {
            method: 'post',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                follow: true,
                unfollow: false
            })
        };

        fetch(urlProfile, fetchBody)
        .then(response => {
            if (response.status == 204){
                followBtn.style.display = 'none';
                unfollowBtn.style.display = 'inline-block';
                updateFollowersCount = parseInt(followersCount.innerHTML) + 1;
                followersCount.innerHTML = `${updateFollowersCount}`;
            }
        })
        .then(result => console.log(result))
        .catch(error => {
            console.log("error: ", error);
        })
    });

    unfollowBtn.addEventListener('click', () => {
        const urlProfile = `${parseInt(userProfile)}`;
        const fetchBody = {
            method: 'post',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                follow: false,
                unfollow: true
            })
        };

        fetch(urlProfile, fetchBody)
        .then(response => {
            if (response.status == 204){
                unfollowBtn.style.display = 'none';
                followBtn.style.display = 'inline-block';
                updateFollowersCount = parseInt(followersCount.innerHTML) - 1;
                followersCount.innerHTML = `${updateFollowersCount}`;
            }
        })
        .then(result => console.log(result))
        .catch(error => {
            console.log("error: ", error);
        })
        return false;
    });
})
