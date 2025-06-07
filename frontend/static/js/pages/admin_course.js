document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("addCourseForm");
    const addCourseBtn=document.getElementById("addCourse")
    // const loadingSpinner = document.getElementById("loadingSpinner");
    if (!form) return;
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
  
      // Remove previous alerts
      document.querySelectorAll('.alert').forEach(alertEl => alertEl.remove());
  
      // Create a FormData object to send multipart/form-data
      const formData = new FormData(form);
      // Show the spinner and change the button text to "Processing..."
    // loadingSpinner.style.display = "inline-block";
    addCourseBtn.innerHTML = 'Adding Course... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
  
      try {
        const response = await fetch("/api/admin/courses/add", {
          method: "POST",
          body: formData
        });
  
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText);
        }
  
        const data = await response.json();
        // data should contain the newly added course details
  
        const alertDiv = document.createElement("div");
        alertDiv.className = "alert alert-success";
        alertDiv.innerHTML = `Course "${data.title}" added successfully!`;
        form.prepend(alertDiv);
        form.reset();
        addCourseBtn.innerHTML = "Add Course";
      } catch (error) {
        console.error("Error adding course:", error);
        const errorAlert = document.createElement("div");
        errorAlert.className = "alert alert-danger mt-3";
        errorAlert.textContent = error.message || "Failed to add course. Please try again.";
        form.prepend(errorAlert);

        // Hide the spinner and reset button text
        // loadingSpinner.style.display = "none";
        addCourseBtn.innerHTML = "Add Course";
      }
    });
  });  