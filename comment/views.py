# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from comment.models import Comment
# import json

# @login_required
# @csrf_exempt
# def edit_comment(request, comment_id):
#     if request.method == "POST":
#         try:
#             # Get the comment belonging to the user
#             comment = get_object_or_404(Comment, id=comment_id, user=request.user)
#             print(f'body: {comment.body}')
#             print(f'id: {comment}')
            
#             # Parse JSON data
#             try:
#                 data = json.loads(request.body)
#                 new_body = data.get('body', '').strip()
#             except json.JSONDecodeError:
#                 return JsonResponse({"success": False, "error": "Invalid JSON format."})

#             # Validate new body
#             if not new_body:
#                 return JsonResponse({"success": False, "error": "Comment body cannot be empty."})

#             # Update and save the comment
#             comment.body = new_body
#             comment.save()
#             return JsonResponse({"success": True, "new_body": new_body})

#         except Comment.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Comment not found or unauthorized."})
#     return JsonResponse({"success": False, "error": "Invalid request method."})


# @login_required
# @csrf_exempt
# def delete_comment(request, comment_id):
#     if request.method == "POST":
#         try:
#             # Get the comment belonging to the user
#             comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            
#             # Delete the comment
#             comment.delete()
#             return JsonResponse({"success": True})

#         except Comment.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Comment not found or unauthorized."})
#     return JsonResponse({"success": False, "error": "Invalid request method."})
