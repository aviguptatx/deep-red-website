function updateLineNumbers() {
    const textArea = document.getElementById('text');
    const lineNumbers = document.getElementById('line-numbers');
    
    const linesCount = textArea.value.split('\n').length;
    lineNumbers.innerHTML = Array.from(Array(linesCount), (_, i) => `<span>${i + 1}</span>`).join('');
    
    lineNumbers.style.transform = `translateY(-${textArea.scrollTop}px)`;
    
    const textAreaRect = textArea.getBoundingClientRect();
    const firstVisibleLineNumber = Math.ceil(textArea.scrollTop / 20) + 1;
    const lastVisibleLineNumber = firstVisibleLineNumber + Math.ceil(textAreaRect.height / 20) - 1;
    
    const lineNumberSpans = lineNumbers.querySelectorAll('span');
    lineNumberSpans.forEach((span, index) => {
        if (index + 1 < firstVisibleLineNumber || index + 1 > lastVisibleLineNumber) {
            span.style.visibility = 'hidden';
        } else {
            span.style.visibility = 'visible';
        }
    });
}

function insertTemplate() {
    const templateInput = `SEAT 4
1111111 - 15 RRB RR R
1111111 - 26 RRB RB B
1111111 - 37 RRR RR R - INV 7 FAS
0000000 - 46
0000000 - 51
1111111 - 62 RRR RR R - SE 2
1111111 - 24 RBB BB B
0000000 - 71
1000000 - 15
1111000 - 23 RRR RR R - KILL 7
1111000 - 34 RBB RB B
1001010 - 46
0110000 - 52
0001000 - 62 B
1001000 - 13
1110110 - 23 RRR RR R - KILL 4
0110100 - 52 H`;
    const textarea = document.getElementById('text');
    textarea.value = templateInput;
    updateLineNumbers();
}

function validateInput(text) {
    const lines = text.trim().split('\n');

    updateLineNumbers();

    if (!/^SEAT \d+$/.test(lines[0])) {
        return 'Invalid input format. The first line should start with "SEAT" followed by a space and the seat number.';
    }

    if (lines.length < 2) {
        return 'Invalid input. Please provide at least one line of input after the seat number.';
    }

    for (let i = 1; i < lines.length; i++) {
        const line = lines[i];

        if (!/^\d{7} - \d{2}( [ A-Z]+)?( - (INV|SE|KILL).+)?$/.test(line)) {
            return `Invalid input format on line ${i + 1}. Please check the format and try again.`;
        }
    }

    return null;
}

function predict() {
    const text = document.getElementById('text').value;
    const resultDiv = document.querySelector('.result-container');
    resultDiv.innerHTML = '';
    const errorDiv = document.createElement('div');

    const validationError = validateInput(text);
    if (validationError) {
        errorDiv.classList.add('error');
        errorDiv.innerText = validationError;
        resultDiv.appendChild(errorDiv);
        return;
    }

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);

        const prediction = data.prediction;

        const barsContainer = document.createElement('div');
        barsContainer.classList.add('bars-container');

        if (prediction.length === 0) {
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('error');
            errorDiv.innerHTML = '<p>Invalid input. Please check the format and try again.</p>';
            resultDiv.appendChild(errorDiv);
        } else {
            for (let i = 0; i < prediction.length; i++) {
                const person = document.createElement('div');
                person.classList.add('person');
                const color = interpolateColor(prediction[i]);
                person.style.backgroundColor = color;
    
                const label = document.createElement('div');
                label.classList.add('label');
                label.innerText = `Seat ${i + 1}: ${prediction[i].toFixed(2)}`;
                label.style.color = isDarkColor(color) ? 'white' : 'black';
    
                person.appendChild(label);
                barsContainer.appendChild(person);
            }
        }
        resultDiv.appendChild(barsContainer);
    })
    .catch(error => {
        errorDiv.classList.add('error');
        errorDiv.innerText = "Server Error. Perhaps your game is too long?";
        resultDiv.appendChild(errorDiv);
    });
    updateLineNumbers();
}

function interpolateColor(value) {
    const blue = [0, 0, 255];
    const purple = [128, 0, 255];
    const red = [255, 0, 0];

    if (value <= 0.5) {
        const t = value * 2;
        const color = blue.map((c, i) => Math.round(c + (purple[i] - c) * t));
        return `rgb(${color.join(',')})`;
    } else {
        const t = (value - 0.5) * 2;
        const color = purple.map((c, i) => Math.round(c + (red[i] - c) * t));
        return `rgb(${color.join(',')})`;
    }
}

function isDarkColor(color) {
    const rgb = color.match(/\d+/g);
    const brightness = Math.round(
        (parseInt(rgb[0]) * 299 +
        parseInt(rgb[1]) * 587 +
        parseInt(rgb[2]) * 114) / 1000
    );
    return brightness <= 125;
}

document.getElementById('text').addEventListener('scroll', updateLineNumbers);
window.addEventListener('resize', updateLineNumbers);
