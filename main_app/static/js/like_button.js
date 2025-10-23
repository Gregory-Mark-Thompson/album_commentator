document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.like-button');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            
            fetch(`/comment/${commentId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
            })
            .then(response => response.json())
            .then(data => {
                // Update button text and state
                this.textContent = data.liked ? 'Unlike' : 'Like';
                this.setAttribute('data-liked', data.liked);
                
                // Update like count
                const likeCountElement = this.parentElement.querySelector('.like-count');
                likeCountElement.textContent = data.like_count;
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    function getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});