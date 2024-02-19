document.addEventListener("DOMContentLoaded", function () {
    var loginButton = document.getElementById("loginButton");
    var actionDropdown = document.getElementById("actionDropdown");
    var logintime;
    var logofftime;
    var breakStartTime;
    var breakendtime;
    var meetingendtime;
    var downtimeendtime;
    var meetingStartTime;
    var downtimeStartTime;
    var totalbreakTime;
    var totalmeetingTime;
    var totaldownTime;
    var totalbreakTimex = 0;
    var totalmeetingTimex = 0;
    var totaldownTimex = 0;
    var totalbreak = 0;
    var totalmeeting = 0;
    var totaldown = 0;
    var totalfree = 0;
    var totallog;
    var totallogx;
    var totalwork;
    var totalworkx;
    var totalworkz;
    // Retrieve the stored button text from localStorage
    var storedButtonText = localStorage.getItem("buttonText");
  
    // Set the initial state based on the stored value
    if (storedButtonText) {
      loginButton.innerText = storedButtonText;
      if (storedButtonText === "ACTION") {
        loginButton.style.backgroundColor = "#335810fa";
      }
    }
  
    // Hide the dropdown initially
    actionDropdown.style.display = "none";
  
    loginButton.addEventListener("click", function (event) {
      if (loginButton.innerText === "LOGIN") {
        logintime = new Date(); // Capture login time
        loginButton.innerText = "ACTION";
        loginButton.style.backgroundColor = "#335810fa";
        actionDropdown.style.display = "none";
  
        // Store the current button text in localStorage
        localStorage.setItem("buttonText", "ACTION");
      } else if (loginButton.innerText === "ACTION") {
        // Toggle between dropdown and logoff
        actionDropdown.style.display =
          actionDropdown.style.display === "block" ? "none" : "block";
  
        // Position the dropdown to the right end of the page with an additional 10 pixels
        var rightEdge =
          document.documentElement.clientWidth -
          loginButton.getBoundingClientRect().right;
        actionDropdown.style.right = rightEdge + 10 + "px";
  
        // Prevent default action (e.g., submitting a form or following a link)
        event.preventDefault();
      } else {
        if (loginButton.innerText === "BREAK TIME") {
          // Toggle between dropdown and logoff
          breakendtime = new Date();
          totalbreakTime = breakendtime - breakStartTime;
          totalbreak = totalbreak + totalbreakTime;
          totalbreakTimex = formatTimeDifference(totalbreak);
          display();
        } else if (loginButton.innerText === "MEETING") {
          // Toggle between dropdown and logoff
          meetingendtime = new Date();
          totalmeetingTime = meetingendtime - meetingStartTime;
          totalmeeting = totalmeeting + totalmeetingTime;
          totalmeetingTimex = formatTimeDifference(totalmeeting);
          display();
        } else if (loginButton.innerText === "DOWN TIME") {
          // Toggle between dropdown and logoff
          downtimeendtime = new Date();
          totaldownTime = downtimeendtime - downtimeStartTime;
          totaldown = totaldown + totaldownTime;
          totaldownTimex = formatTimeDifference(totaldown);
          display();
        }
  
        logofftime = new Date(); // Capture logoff time
        loginButton.innerText = "ACTION";
        loginButton.style.backgroundColor = "";
        actionDropdown.style.display = "none";
  
        // Remove the stored button text when switching back to LOGIN
        localStorage.removeItem("buttonText");
        localStorage.setItem("buttonText", "ACTION");
  
        // Send login and logoff times to Django (adapt this part based on your backend setup)
        sendTimesToBackend(
          logintime,
          logofftime,
          totalbreakTimex,
          totalmeetingTimex,
          totaldownTimex,
          totalwork
        );
      }
    });
  
    actionDropdown.addEventListener("click", function (event) {
      if (event.target.matches(".btn-dropdown-item")) {
        if (event.target.innerText == "LOGOFF") {
          logofftime = new Date(); // Capture logoff time
          loginButton.innerText = "LOGIN";
          localStorage.setItem("buttonText", "LOGIN");
          totalfree = totalbreak + totalmeeting + totaldown;
          totallog = logofftime - logintime;
  
          totalwork = totallog - totalfree;
  
          totalworkx = formatTimeDifference(totalwork);
          totallogx = formatTimeDifference(totallog);
          // Send login and logoff times to Django (adapt this part based on your backend setup)
          sendTimesToBackend(
            logintime,
            logofftime,
            totalbreakTimex,
            totalmeetingTimex,
            totaldownTimex,
            totalwork
          );
        } else {
          // Update start time based on the selected action
          switch (event.target.innerText) {
            case "BREAK TIME":
              breakStartTime = new Date();
              break;
            case "MEETING":
              meetingStartTime = new Date();
  
              break;
            case "DOWN TIME":
              downtimeStartTime = new Date();
  
              break;
            // ... (add cases for other actions)
          }
          //console.log(breakStartTime,meetingStartTime,downtimeStartTime);
  
          loginButton.innerText = event.target.innerText;
          console.log("loginButton.innerText : ", loginButton.innerText);
          localStorage.setItem("buttonText", event.target.innerText);
        }
        display();
        actionDropdown.style.display = "none";
        loginButton.style.backgroundColor = "";
      }
    });
  
    document.addEventListener("click", function (event) {
      if (
        !event.target.matches("#loginButton") &&
        !event.target.matches(".btn-dropdown-item")
      ) {
        if (loginButton.innerText === "ACTION") {
          //logofftime = new Date(); // Capture logoff time
          loginButton.innerText = "LOGIN";
          loginButton.style.backgroundColor = "";
  
          // Remove the stored button text when switching back to LOGIN
          //localStorage.removeItem("buttonText");
  
          // Send login and logoff times to Django (adapt this part based on your backend setup)
          //sendTimesToBackend(logintime, logofftime);
        }
        actionDropdown.style.display = "none";
      }
      console.log("logintime : ", logintime);
      console.log("logoffitme : ", logofftime);
    });
  
    actionDropdown.addEventListener("click", function (event) {
      event.stopPropagation();
    });
    function toISOStringUTC(date) {
      return new Date(
        date.getTime() - date.getTimezoneOffset() * 60000
      ).toISOString();
    }
    function sendTimesToBackend(
      logintime,
      logofftime,
      totalbreakTimex,
      totalmeetingTimex,
      totaldownTimex,
      totalworkx
    ) {
      // Get the CSRF token from the cookies
      var csrftoken = getCookie("csrftoken");
      totalworkz = formatTimeDifference(totalworkx);
      console.log("total logintime send too the backend  : ", logintime);
      var logintimeString = toISOStringUTC(logintime);
      var logofftimeString = toISOStringUTC(logofftime);
      var dataToSend = {
        logintime: logintimeString,
        logofftime: logofftimeString,
        totalbreakTimex: totalbreakTimex,
        totalmeetingTimex: totalmeetingTimex,
        totaldownTimex: totaldownTimex,
        totalworkx: totalworkz,
      };
  
      fetch("/logentry", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken, // Include the CSRF token in the headers
        },
        body: JSON.stringify(dataToSend),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          console.log(data);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  
    // Function to get the CSRF token from cookies
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          // Check if the cookie name matches the expected format
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  
    function formatTimeDifference(timeDifference) {
      // Convert time difference to seconds, minutes, and hours
      var seconds = Math.floor(timeDifference / 1000);
      var minutes = Math.floor(seconds / 60);
      var hours = Math.floor(minutes / 60);
  
      // Calculate remaining seconds and minutes after converting to hours
      var remainingSeconds = seconds % 60;
      var remainingMinutes = minutes % 60;
  
      // Format the time as "hh:mm:ss"
      var formattedTime =
        hours + " hr " + remainingMinutes + " min " + remainingSeconds + " sec";
  
      return formattedTime;
    }
  
    function addTimeDurations(time1, time2) {
      // Parse hours, minutes, and seconds from the formatted time strings
      var regex = /(\d+) hr (\d+) min (\d+) sec/;
      var match1 = time1.match(regex);
      var match2 = time2.match(regex);
  
      // Calculate the total hours, minutes, and seconds
      var totalHours = parseInt(match1[1]) + parseInt(match2[1]);
      var totalMinutes = parseInt(match1[2]) + parseInt(match2[2]);
      var totalSeconds = parseInt(match1[3]) + parseInt(match2[3]);
  
      // Adjust for overflow
      totalMinutes += Math.floor(totalSeconds / 60);
      totalSeconds %= 60;
      totalHours += Math.floor(totalMinutes / 60);
      totalMinutes %= 60;
  
      // Format the total time as "hh:mm:ss"
      var formattedTotalTime =
        totalHours + " hr " + totalMinutes + " min " + totalSeconds + " sec";
  
      return formattedTotalTime;
    }
  
    function display() {
      //var hoursDifference = minutesDifference / 60;
  
      console.log("================================");
      console.log("total logintime : ", logintime);
      console.log("totoal breakendtime : ", totalbreakTimex);
      console.log("total meetingstarttime : ", totalmeetingTimex);
      console.log("total downstarttime : ", totaldownTimex);
      console.log("total log time : ", totallogx);
      console.log("total work time : ", totalworkx);
      console.log("================================");
    }
  });
  