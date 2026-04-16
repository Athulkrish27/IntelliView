import torch
import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1

class FaceRecognition:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
    
    def get_face_matrix(self, image_path):
        """Process image from file path"""
        image = cv2.imread(image_path)
        return self._extract_face_embedding(image)

    def get_face_matrix_from_numpy(self, image_np):
        """Process image from NumPy array (useful for Django's request.FILES)"""
        return self._extract_face_embedding(image_np)

    def _extract_face_embedding(self, image):
        """Internal method to extract face embeddings from an image"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        faces, _ = self.mtcnn.detect(image_rgb)
        if faces is None:
            raise ValueError("No face detected in the image")
        
        face_crops = self.mtcnn(image_rgb)
        face_crops = face_crops.to(self.device)
        face_embedding = self.model(face_crops).detach().cpu().numpy()
        
        return face_embedding[0]  # Return the first face encoding

    def compare_faces(self, face_matrix1, face_matrix2, threshold=0.95):
        """Compare two face matrices and return True if they match"""
        face_matrix1 = np.array(face_matrix1)
        face_matrix2 = np.array(face_matrix2)

        distance = np.linalg.norm(face_matrix1 - face_matrix2)
        return distance < threshold


    def detect_and_compare(self, image_path1, image_path2):
        """Compare faces from two image paths"""
        face1 = self.get_face_matrix(image_path1)
        face2 = self.get_face_matrix(image_path2)
        return self.compare_faces(face1, face2)

"""
# Example Usage
face_rec = FaceRecognition()
face_matrix1 = face_rec.get_face_matrix("anne.jpg")
face_matrix2 = face_rec.get_face_matrix("anne2.jpg")
result = face_rec.compare_faces(face_matrix1, face_matrix2)


# Convert uploaded image to NumPy array
pro_pic_file = request.FILES['pro_pic'].read()  # Read image bytes
image_pil = Image.open(BytesIO(pro_pic_file))  # Open as PIL image
image_np = np.array(image_pil)  # Convert to NumPy array

# Generate face matrix without saving the image
face_recognizer = FaceRecognition()
face_matrix = face_recognizer.get_face_matrix_from_numpy(image_np)

# Convert face matrix to JSON-storable format
table.face_matrix = face_matrix.tolist()



"""