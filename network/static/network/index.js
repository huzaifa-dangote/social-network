function edit_post(post_id) {

    // Display pop-up box to allow editing
    document.querySelector('#edit-post-box').style.display = 'block';

    // Declare variable for post textarea
    const post_content = document.querySelector('#edit-post-field');

    // GET post data
    fetch(`/edit/${post_id}`)
    .then(response => response.json())
    .then(post => {
        console.log(post);

        // Pre-fill post textarea
        post_content.value = `${post.content}`;
    })

    // Save edited post
    document.querySelector('#edit-post-form').addEventListener('submit', event => {
        fetch(`/edit/${post_id}`, {
            method: 'PUT',
            body: JSON.stringify({
                content: post_content.value
            })
        })

        // GET updated post and update page
        fetch(`/edit/${post_id}`)
        .then(response => response.json())
        .then(post => {
            console.log(post);
            document.querySelector(`#post-display-${post_id}`).innerHTML = post.content;
        })

        event.preventDefault();

        // Close modal
        document.querySelector('#edit-post-box').style.display = 'none';
    })
}

function like_unlike_post(user, post_id) {
    fetch(`/edit/${post_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            liked_by: user
        })
    })

    // Update like count
    setTimeout(() => update_likes(), 20);
}

function update_likes() {
    fetch(`/edit/${post_id}`)
    .then(response => response.json())
    .then(post => {
        console.log(post);
        document.querySelector(`#post-likes-${post_id}`).innerHTML = `${post.likes}`;
    })

    // Change like button to unlike or like
    const like_button = document.querySelector(`#like-button-${post_id}`);
    
    if (like_button.innerHTML === 'Like') {
        like_button.innerHTML = 'Unlike';
    }
    else {
        like_button.innerHTML = 'Like';
    }
}