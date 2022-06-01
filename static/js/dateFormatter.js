
let monthToDay={
    "01":'January',
    "02":'February',
    "03":'March',
    "04":'April',
    "05":'May',
    "06":'June',
    "07":'July',
    "08":'August',
    "09":'September',
    "10":'October',
    "11":'November',
    "12":'December'
}
let dateArr = document.currentScript.getAttribute('date').split('-');
console.log(dateArr)
console.log(dateArr[1])
let month = monthToDay[dateArr[1]]
console.log(month)
var monthTag = document.getElementById(document.currentScript.getAttribute('monthTag'));
let ext;
let dateDay = dateArr[2]
console.log(dateDay)
if(dateDay%10 ==1){
    ext = 'st'
}
else if (dateDay%10 == 2){
    ext='nd'
}
else {
    ext='th'
}
if(dateDay<10){
    dateDay = dateDay%10
}
heading = dateDay+ ext+ ' ' + month + ' ' +dateArr[0]+'!'
monthTag.innerHTML= heading;