// document.addEventListener("DOMContentLoaded", () => {
//     const logoutBtn = document.getElementById("logoutBtn");
//     if (!logoutBtn) return;
    
//     // Retrieve CSRF token from the meta tag
//     const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
//     const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute("content") : null;
    
//     logoutBtn.addEventListener("click", async () => {
//       try {
//         const response = await fetch("/api/auth/logout", {
//           method: "POST",
//           headers: { 
//             "Content-Type": "application/json",
//             "X-CSRF-Token": csrfToken, // use the CSRF token here
//           }
//         });
        
//         if (!response.ok) {
//           const data = await response.json();
//           throw new Error(data.detail || "Logout failed");
//         }
        
//         // On successful logout, redirect to the login page
//         window.location.href = "/login";
//       } catch (error) {
//         alert("Logout error: " + error.message);
//         console.error("Logout error:", error);
//       }
//     });
//   });
  

  document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logoutBtn");
    if (!logoutBtn) return;
    // Retrieve CSRF token from the meta tag
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute("content") : null;
  
    logoutBtn.addEventListener("click", async (e) => {
      e.preventDefault();
  
      try {
          const response = await fetch("/api/auth/logout", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken,
          },
        });
  
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || "Logout failed");
        }
  
        window.location.href = "/login";
      } catch (err) {
        alert("Logout error: " + err.message);
        console.error("Logout error:", err);
      }
    });
  
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(";").shift();
    }
  });
  