const navToggle = document.querySelectorAll(".nav-toggle");
const sidebar = document.querySelector(".sidebar");
const navIcon = document.querySelectorAll(".navIcon");
const hamburger = document.querySelector("#hamburger");
const body = document.querySelector(".body");

// Shows mobile and tablet navigation menu
navToggle.forEach(item => {
  item.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    body.classList.toggle("back-color")
    navIcon.forEach(icon => {
        icon.classList.toggle("hidden");
    })
})})

// Put the month the user is looking at in the calendar into local storage
let month = document.querySelector(".month")
if (month) {
  localStorage.setItem("month", month.innerHTML);
} 

// Empty local storage when user logs out
let logout = document.querySelector("#logout")
logout.addEventListener("click", function() {
  localStorage.removeItem("selectedDate");
  localStorage.removeItem("year");
  localStorage.removeItem("selectedTime");
})

// Put the year into local storage
let year = document.querySelector(".year")
if (year) {
  localStorage.setItem("year", year.innerHTML);
} 

let bookingLinks = document.querySelectorAll(".bookingLink")
let times = document.querySelectorAll(".timeslot")
let cancelButtons = document.querySelectorAll(".cancel")

// Add event listener to all days on the calendar view
bookingLinks.forEach((bookingLink) => {
  bookingLink.addEventListener("click",  function() {
    localStorage.setItem("selectedDate", bookingLink.innerHTML);
    document.location.href = 'http://localhost:8989/middle'; 
  })
})

// Add event listener to the three different timeslots
times.forEach((time) => {
  time.addEventListener("click",  function() {
    localStorage.setItem("selectedTime", time.innerHTML);
  })
})

// Event listener to back button going to the calendar view, for if user goes back to pick a different day
let backToCal = document.getElementById("backToCal")
if (backToCal) {
  backToCal.addEventListener("click", function() {
    localStorage.removeItem("selectedDate");
  })
}

// Event listener to back button going to the timeslosts view, for if user goes back to pick a different time
let backToDay = document.getElementById("backToDay")
if (backToDay) {
  backToDay.addEventListener("click", function() {
    localStorage.removeItem("selectedTime");
  })
}

let confirmedDay = localStorage.getItem("selectedDate") 
let confirmedMonth = localStorage.getItem("month")
let confirmedYear = localStorage.getItem("year")
let confirmedTime = localStorage.getItem("selectedTime")

function getMonthNumberFromName(monthName) {
  return new Date(`${monthName} 1, 2022`).getMonth();
}

let monthNumber = getMonthNumberFromName(confirmedMonth)

let selectedDay = document.getElementById("selectedDay");
if (selectedDay) {
  selectedDay.value = confirmedDay + '/' + (monthNumber+1).toString() + '/' + confirmedYear
}

let confirmDay = document.getElementById("confirmDay");
if (confirmDay) {
  confirmDay.value = confirmedDay + '/' + (monthNumber+1).toString() + '/' + confirmedYear
}

document.getElementById("confirmTime").value = confirmedTime


