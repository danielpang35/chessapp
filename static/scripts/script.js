let dragged = null;
function drawboard(arr){
    console.log(arr)
    let board = document.getElementsByClassName("board").item(0)
    while(board.firstChild)
    {
        board.removeChild(board.firstChild)
    }
    for (i =7;i>=0;i--)
    {
        for(j = 0;j<8;j++)
        {
            let square = document.createElement("div");
            ind = i*8+j
            square.setAttribute("sqindex",ind)
            img = document.createElement("img")
            img.setAttribute("sqindex",ind)
            if(arr.length != 0)
            {   
                if(arr[ind] != ''){
                    img.className = "piece"
                    piecestr = arr[ind]
                    img.src = "../../static/images/" + piecestr + ".png"
                    img.addEventListener("dragstart",drag)
                    img.setAttribute("draggable", "true")
                    square.appendChild(img)
            }}
            square.addEventListener("click",click)
            square.addEventListener("dragover",allowDrop)
            square.addEventListener("drop",drop)
            let color = (j+i)%2 == 0 ? "darksquare" : "lightsquare"
            board.appendChild(square).className = color
        }
    }
}

function drag(event)
{
    console.log(event.target)
    square = event.target.parentNode
    event.dataTransfer.setData("text",square.getAttribute("sqindex"))
    console.log("began drag at:",square.getAttribute("sqindex"))
    dragged = event.target
    event.dataTransfer.dropEffect = "move"
}
async function drop(event)
{
    event.preventDefault()
    droppedat = event.target.getAttribute("sqindex")
    from = dragged.parentNode.getAttribute("sqindex")

    movedata = {
        fromsquare:from,
        tosquare:droppedat    }
    const res = await fetch("/human", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body:JSON.stringify(movedata)
    })
    response = await res.json()
    board = response["board"]
    console.log("dragged from :",dragged.parentNode.getAttribute("sqindex"), "dropped at",event.target)
    console.log("received: ", board)
    drawboard(board)    
    // if(event.target.className == "lightsquare" ||  event.target.className == "darksquare")
    // {
    //     dragged.parentNode.removeChild(dragged)
    //     event.target.appendChild(dragged)
    // }
}
function allowDrop(event)
{
    event.preventDefault()
    console.log("alloweddrop at index:",event.target.getAttribute("sqindex"))
}
async function click(event) {
    let ret = {index: event.target.getAttribute("sqindex")}

    console.log(ret)
    const res = await fetch("/human", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(ret)
    })
    data = await res.json()
    board = data["board"]
    drawboard(board)
    // .then((response) => response.json())
    // .then((data)=>{
    //     board = data //an array of 64 squares, pieces denoted with corresponding string
    //     drawboard(board)
    //     console.log(board)
    // })
    // let req = new XMLHttpRequest()
    // req.open("POST", "/human", true)
    // req.setRequestHeader('Content-Type', 'application/json');
    // req.send(ret)
}

document.addEventListener("DOMContentLoaded", main)
function main(){
    print
    console.log("HERE", initarray)
    drawboard(initarray)
}