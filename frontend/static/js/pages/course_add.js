document.addEventListener("DOMContentLoaded", () => {
    const courseForm = document.getElementById("courseForm");
  
    courseForm.addEventListener("submit", async (event) => {
      event.preventDefault(); // Stop normal form submission
  
      clearErrorMessages();
  
      // 1. Gather the form data
      const formData = new FormData(courseForm);
      const jsonData = Object.fromEntries(formData.entries());
  
      // (Optional) basic client-side validation
      // e.g. check if fields are empty, rating is in [0,5], etc.
      // If errors, set them on relevant <span> and return
  
      try {
        // 2. POST to your /courses/ API (adjust if your endpoint is different)
        const response = await fetch("/api/courses/add-course/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(jsonData)
        });
  
        if (!response.ok) {
            if (response.status === 422) {
              // Pydantic validation errors
              const errorData = await response.json();
              handleValidationErrors(errorData);
            } else if (response.status === 401 || response.status === 403) {
              // Auth error (e.g. "Could not validate token")
              const errorData = await response.json();
              if (errorData.detail === "Could not validate token") {
                alert("Your session token is invalid or expired. Please log in again.");
              } else {
                alert(`Error: ${errorData.detail || "Unauthorized"}`);
              }
            } else {
              // Other server errors (400, 500, etc.)
              const errorData = await response.json();
              alert(`Error: ${errorData.detail || "Unknown error"}`);
            }
            return;
          }
          
  
        // 4. If success, show the modal
        const createdCourse = await response.json();
        console.log("Course created:", createdCourse);
  
        // Show the Bootstrap modal
        const successModal = new bootstrap.Modal(document.getElementById("successModal"));
        successModal.show();
  
        // 5. Optionally redirect after user closes the modal
        const successCloseBtn = document.getElementById("successCloseBtn");
        successCloseBtn.addEventListener("click", () => {
          window.location.href = "/courses"; // or wherever you want to go
        });
      } catch (error) {
        console.error("Error creating course:", error);
        alert("An error occurred. Check console logs.");
      }
    });
  
    // Helper: Clear error text
    function clearErrorMessages() {
      document.querySelectorAll("#courseForm span.text-danger").forEach(span => {
        span.textContent = "";
      });
    }
  
    // Helper: Handle validation errors from FastAPI (422)
    function handleValidationErrors(errorResponse) {
      if (!errorResponse.detail || !Array.isArray(errorResponse.detail)) {
        alert("Validation error: could not parse details.");
        return;
      }
      errorResponse.detail.forEach(err => {
        // Typically looks like { loc: ["body","price"], msg: "field required", ... }
        const fieldName = err.loc[1]; 
        const fieldErrorElement = document.getElementById(fieldName + "Error");
        if (fieldErrorElement) {
          fieldErrorElement.textContent = err.msg;
        }
      });
    }
  });  