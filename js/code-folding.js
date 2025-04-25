/*
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("pre").forEach(function (preBlock) {
        // Skip processing if it should be shown by default
        const parentDiv = preBlock.parentElement;
        if (parentDiv.classList.contains("show-default")) {
            return;
        }
        // Create a wrapper div
        let container = document.createElement("div");
        container.classList.add("code-toggle-container");

        // Create a button element
        let button = document.createElement("button");
        button.innerHTML = "Show Code";
        button.classList.add("code-toggle");

        // Insert button inside the container
        container.appendChild(button);

        // Insert container before the <pre> block
        preBlock.parentNode.insertBefore(container, preBlock);

        // Hide code initially
        preBlock.style.display = "none";

        // Toggle functionality
        button.addEventListener("click", function () {
            if (preBlock.style.display === "none") {
                preBlock.style.display = "block";
                button.innerHTML = "Hide Code";
            } else {
                preBlock.style.display = "none";
                button.innerHTML = "Show Code";
            }
        });
    });
});
*/


document.addEventListener("DOMContentLoaded", function () {
    
    // Apply syntax highlighting after content is fully loaded
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }
    
    document.querySelectorAll(".highlight").forEach(function (highlightBlock) {
        const pre = highlightBlock.querySelector("pre");
        const code = highlightBlock.querySelector("code");

        if (!pre || !code) return;

        const previousDiv = highlightBlock.previousElementSibling;
        const isShowDefault = previousDiv && previousDiv.classList.contains('show-default')

        // If show-default, don't add code toggle and show by default
        if (isShowDefault) {
            pre.style.display = "block";
        } else {

        // Everything else gets a toggle (no change here)
        const container = document.createElement("div");
        container.classList.add("code-toggle-container");

        const button = document.createElement("button");
        button.classList.add("code-toggle");
        button.innerHTML = "Show Code";

        // Insert button and hide code
        container.appendChild(button);
        highlightBlock.insertBefore(container, pre);
        pre.style.display = "none";

        button.addEventListener("click", function () {
            if (pre.style.display === "none") {
                pre.style.display = "block";
                button.innerHTML = "Hide Code";
            } else {
                pre.style.display = "none";
                button.innerHTML = "Show Code";
            }
        });
        };
    });
});