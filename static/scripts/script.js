let dragged = null;
let selectedPiece = null;
let droppedat = null;
let from = null;
async function sendMove(movedata)
{

    const res = fetch("/human", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body:JSON.stringify(movedata)
    })

    .then((response) => {return response.json()})
    .then((data)=>
    {
        console.log(data)
        if(data["moved"])
        {
            const compresponse = fetch("/com", {
                method: "POST"
            })
            .then((response) => {return response.json()})
            .then((data) =>
            {
                console.log(data)
                from = data['move']['fromsquare']
                droppedat = data['move']['tosquare']
                console.log(from,droppedat)
                drawboard(data['board'])
                drawmetrics(data['data'])
                
            })
        } else {
            from = null;
            droppedat = null;
        }
        drawboard(data["board"])
        
        // console.log(data)
    })
    return
}
function drawmetrics(metrics)
{
    let dashboard = document.getElementsByClassName("metrics").item(0)
    while(dashboard.firstChild)
    {
        dashboard.removeChild(dashboard.firstChild)
    }
    console.log(metrics)
    Object.entries(metrics).map((ele) => {
        let key = ele[0]
        let value = ele[1]
        let metric = document.createElement("div")
        metric.textContent = key + ": "+value
        metric.classList.add('metric')
        console.log(key,value)
        dashboard.appendChild(metric)
    })
    
}

function drawboard(arr){
    dragged = null
    console.log("drawing board:",arr)
    console.log(arr.length)
    let board = document.getElementsByClassName("board").item(0)
    board.id = 'board'
    // document.getElementById('board').style.display = 'none';
    // document.getElementById('board').style.display = 'grid';
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
                if(arr[ind] != ""){
                    console.log(arr[ind])
                    img.className = "piece"
                    piecestr = arr[ind]
                    img.src = "../../static/images/" + piecestr + ".png"
                    if(player &&piecestr.includes("w"))
                    {
                        img.addEventListener("dragstart",drag)
                        img.setAttribute("draggable", "true")
                    }
                    square.appendChild(img)
            }}
            square.addEventListener("dragover",allowDrop)
            square.addEventListener("drop",drop)
            let color = (j+i)%2 == 0 ? "darksquare" : "lightsquare"
            board.appendChild(square).classList.add(color)
            square.classList.add('cell')
            if(ind == droppedat) {
                console.log(ind,droppedat,square)
                square.classList.add('dropped')
            }
            if(ind ==from) {
                square.classList.add('from')
            }
            if(selectedPiece && ind == selectedPiece.getAttribute("sqindex"))
            {
                square.style.backgroundColor = square.parentNode.classList.contains('lightsquare') ? '#ffe6ad': '#ebcc84';
            }
        }
    }
    document.querySelectorAll('.cell').forEach(cell => {
        cell.addEventListener('click', click)}
    )

}


function drag(event)
{
    console.log(event.target)
    square = event.target.parentNode
    event.dataTransfer.setData("text",square.getAttribute("sqindex"))
    console.log("began drag at:",square.getAttribute("sqindex"))
    dragged = event.target
    from = dragged.getAttribute("sqindex")
    event.dataTransfer.dropEffect = "none"
}
async function drop(event)
{
    event.preventDefault()
    

    droppedat = event.target.getAttribute("sqindex")
    from = dragged.parentNode.getAttribute("sqindex")
    movedata = {
        fromsquare:from,
        tosquare:droppedat}
    if(droppedat == from)
    {
        return
    }
    arr = []
    await sendMove(movedata)
    
    
    // response = await res.json()
    //board = response["board"]
    //moved = response["moved"]
    console.log("dragged from :",dragged.parentNode.getAttribute("sqindex"), "dropped at",event.target)
    //console.log("received: ", board)
    //drawboard(board)
    // if(moved){
    //     //now wait for computer move
    //     const getCompMove = await fetch("/com", {
    //         method: "POST",
    //     })
    //     compmove = await getCompMove.json()
    //     newboard = response["board"]
    //     console.log("comp played board: ", newboard)
    //     drawboard(newboard)
    // }

    

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
    square = event.target
    if (!selectedPiece) {
        if(square.classList.contains('piece')){
        selectedPiece = square;
        square.style.backgroundColor = square.parentNode.classList.contains('lightsquare') ? '#ffe6ad': '#ebcc84'; // Highlight selected piece
        }else {
            return
        }
    } else {
    // Move the selected piece to the clicked cell
        tosquare = square.getAttribute("sqindex")
        fromsquare = selectedPiece.getAttribute("sqindex")
        droppedat = tosquare
        from = fromsquare
        movedata = {fromsquare:fromsquare,tosquare:tosquare}
        console.log(String(square.src))
        if(fromsquare == tosquare) {
            console.log("unhighlighting",square)
            square.style.backgroundColor = square.parentNode.classList.contains('lightsquare') ? '#f0d9b5' :'#b58863'
            selectedPiece = null
            return
        };

        if(String(square.src).includes("w") && player)
        {
            //this means white selected a piece, then selected another one of its pieces.
            //just set selectedPiece
            selectedPiece.style.backgroundColor = selectedPiece.parentNode.classList.contains('lightsquare') ? '#f0d9b5' :'#b58863'
            selectedPiece = square
            square.style.backgroundColor = square.parentNode.classList.contains('lightsquare') ? '#ffe6ad': '#ebcc84'; // Highlight selected piece
            return
        }
        
        square.innerHTML = selectedPiece.innerHTML;
        selectedPiece.innerHTML = '';
        await sendMove(movedata)
        square.style.backgroundColor = square.parentNode.classList.contains('lightsquare') ? '#b58863' :'#f0d9b5'
        selectedPiece = null;

    }

    
    
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

async function selfplay()
{
    const request = await fetch("/com",{
        method: "POST"
    })
    response = await request.json()
    console.log(response)
}
document.addEventListener("DOMContentLoaded", main)
function main(){
    root = document.getRootNode()
    console.log("HERE", initarray, player)
    drawboard(initarray)
}