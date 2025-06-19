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