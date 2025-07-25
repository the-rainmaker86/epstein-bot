import praw
import openai
from reddit_api_key import key
import time
from reddit_utils import reddit, get_full_context

# Initialize Reddit instance
# reddit = praw.Reddit(
#     client_id='your_client_id',
#     client_secret='your_client_secret',
#     user_agent='your_user_agent'
# )

class TreeNode:
    def __init__(self, val=0, children=None):
        self.val = val
        self.children = children if children is not None else []

def find_rightmost_leaf_of_rightmost_tree(trees):
    """
    Given a list of n-ary trees, returns the rightmost node of the rightmost tree that has no child nodes.
    
    Args:
        trees (list[TreeNode]): List of tree roots
        
    Returns:
        TreeNode: The rightmost leaf node of the rightmost tree, or None if no such node exists
    """
    if not trees:
        print("No trees provided")
        return None
        
    # Sort trees by their root comment's score in descending order
    sorted_trees = sorted(trees, key=lambda x: x.val.score, reverse=True)
    
    # Start with the highest scoring tree
    current_tree = sorted_trees[0]
    print(f"Starting with tree root score: {current_tree.val.score}")
    
    # If the tree is empty, return None
    if not current_tree:
        print("Tree is empty")
        return None
        
    # Helper function to find the rightmost leaf in a tree
    def find_rightmost_leaf(node):
        print(f"Checking node with score: {node.val.score}")
        
        # If this is a leaf node, return it
        if not node.children:
            print(f"Found leaf node with score: {node.val.score}")
            return node
            
        # Sort children by score in descending order
        sorted_children = sorted(node.children, key=lambda x: x.val.score, reverse=True)
        print(f"Sorted children scores: {[child.val.score for child in sorted_children]}")
        
        # Try each child in order of score
        for child in sorted_children:
            result = find_rightmost_leaf(child)
            if result:
                return result
                
        print("No leaf nodes found in this branch")
        return None
        
    result = find_rightmost_leaf(current_tree)
    if result:
        print(f"Final result: node with score {result.val.score}")
    else:
        print("No suitable leaf node found")
    return result

def build_comment_trees(submission_id):
    """
    Builds trees from a Reddit submission, where each node represents a comment.
    
    Args:
        submission_id (str): The ID of the submission to build trees from
        
    Returns:
        list[TreeNode]: List of tree roots, where each tree represents a top-level comment
                       and its reply chain
    """
    trees = []
    
    # Get the submission
    submission = reddit.submission(id=submission_id)
    
    # Load all comments
    submission.comments.replace_more(limit=None)
    
    # Sort top-level comments by score in descending order
    sorted_comments = sorted(submission.comments, key=lambda x: x.score, reverse=True)
    
    # Helper function to build a tree from a comment and its replies
    def build_tree(comment):
        # Create a node for the current comment
        node = TreeNode(val=comment)
        
        # Get all replies to this comment
        comment.refresh()
        replies = list(comment.replies)
        
        # Sort replies by score in descending order
        sorted_replies = sorted(replies, key=lambda x: x.score, reverse=True)
        
        # Recursively build trees for each reply
        for reply in sorted_replies:
            child_tree = build_tree(reply)
            node.children.append(child_tree)
            
        return node
    
    # Build trees for each top-level comment
    for top_level_comment in sorted_comments:
        trees.append(build_tree(top_level_comment))
    
    return trees

def generate_and_post_response(submission_id):
    """
    Generates a ChatGPT response to the rightmost leaf comment and posts it.
    
    Args:
        submission_id (str): The ID of the submission to process
        
    Returns:
        praw.models.Comment: The posted reply comment
    """
    # Build trees from the submission
    trees = build_comment_trees(submission_id)
    
    # Find the rightmost leaf comment
    target_comment = find_rightmost_leaf_of_rightmost_tree(trees)
    if not target_comment:
        print("No suitable comment found to reply to")
        return None
    
    # Get the full context of the comment
    context_comments = get_full_context(target_comment.val)
    
    # Sort parent comments by score in descending order
    sorted_context = sorted(context_comments, key=lambda x: x.score, reverse=True)
    
    # Build the context string for ChatGPT
    context_string = f"Post Title: {target_comment.val.submission.title}\n\n"
    for parent in sorted_context:  # Now ordered by score (best)
        context_string += f"Parent Comment (Score: {parent.score}): {parent.body}\n\n"
    context_string += f"Target Comment (Score: {target_comment.val.score}): {target_comment.val.body}"
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=key)
    
    # Generate response using ChatGPT
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant responding to Reddit comments. Keep your responses concise and relevant to the conversation."},
                {"role": "user", "content": context_string}
            ],
            max_tokens=150
        )
        reply_text = response.choices[0].message.content
        
        print("Context string: ", context_string)
        print("Reply: ", reply_text)
        
        # Post the response to Reddit
        reply = target_comment.val.reply(reply_text)
        print(f"Successfully posted response to comment {target_comment.val.id}")
        return reply
    except Exception as e:
        print(f"Error generating or posting response: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    # Get r/all and sort by top posts from the last hour
    ids = []
    subreddit = reddit.subreddit("all")
    top_posts = subreddit.top(time_filter="hour", limit=25)  # Get top posts from the last hour
    
    # Process each post
    for submission in top_posts:
        # Skip posts from r/Conservative
        if submission.subreddit.display_name.lower() == "conservative":
            print(f"\nSkipping post from r/Conservative: {submission.title}")
            continue
        if submission.subreddit.display_name.lower() in subs:
            print(f"\nSkipping post from r/{submission.subreddit.display_name}: {submission.title}")
            continue
            
        print(f"\nProcessing post: {submission.title}")
        print(f"Score: {submission.score}")
        print(f"URL: https://reddit.com{submission.permalink}")
        
        if submission.id in ids:
            continue
        ids.append(submission.id)
        
        try:
            response = generate_and_post_response(submission.id)
            if response:
                print("Generated response successfully")
                time.sleep(60)
            else:
                print("No response generated")
        except Exception as e:
            print(f"Error processing post {submission.id}: {e}")
            continue

# Example: Print the body of each comment in the first tree
def print_tree(node, depth=0):
    print('  ' * depth + node.val.body)
    for child in node.children:
        print_tree(child, depth + 1)

# if trees:
#     print_tree(trees[0]) 
