
// Function to initialize Tagify and Tribute
function initializeTagifyAndTribute() {
    // Fetch talents, tags, traits, and NPCs data from the API
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {

            // Initialize Tagify for the tags input field
            const tagsInput = document.getElementById('npc-tags');
            if (tagsInput) {
                window.tagifyTags = new Tagify(tagsInput, {
                    whitelist: data.tags || [],  // Use the tags from tags.json
                    dropdown: {
                        enabled: 0,
                        maxItems: 5
                    },
                    enforceWhitelist: false  // Allow adding custom tags
                });

                // Initialize auto-save for tag add/remove events
                window.tagifyTags.on('add', function() {
                    console.log("Tagify Tags: Add event triggered");
                    triggerAutoSave();  // Trigger auto-save on tag add
                });

                window.tagifyTags.on('remove', function() {
                    console.log("Tagify Tags: Remove event triggered");
                    triggerAutoSave();  // Trigger auto-save on tag remove
                });

                window.tagifyTags.on('blur', function() {
                    console.log("Tagify Tags: Blur event triggered");
                    triggerAutoSave();  // Trigger auto-save on blur
                });
            }

            // Initialize Tagify for the talents input field
            const talentsInput = document.getElementById('npc-talents');
            if (talentsInput) {
                window.tagifyTalents = new Tagify(talentsInput, {
                    whitelist: data.talents || [],
                    enforceWhitelist: true,
                    dropdown: {
                        enabled: 0,
                        maxItems: 5
                    }
                });

                window.tagifyTalents.on('blur', function() {
                    console.log("Tagify Talents: Blur event triggered");
                    triggerAutoSave();
                });
            }

            // Initialize Tagify for the traits input field
            const traitsInput = document.getElementById('npc-traits');
            if (traitsInput) {
                window.tagifyTraits = new Tagify(traitsInput, {
                    whitelist: data.traits || [],
                    enforceWhitelist: true,
                    dropdown: {
                        enabled: 0,
                        maxItems: 5
                    }
                });

                window.tagifyTraits.on('blur', function() {
                    console.log("Tagify Traits: Blur event triggered");
                    triggerAutoSave();
                });
            }

            // Initialize Tribute.js for NPC mentions
            const tribute = new Tribute({
                trigger: '@',
                values: data.npcs.map(npc => ({
                    key: npc.name,
                    value: npc.id
                })),
                selectTemplate: function (item) {
                    // Output a link instead of plain text for mentions
                    return `<a href="#" class="npc-mention" data-id="${item.original.value}">${item.original.key}</a>`;
                },
                menuItemTemplate: function (item) {
                    return `${item.original.key}`;
                }
            });

            // Attach Tribute.js to the summary and info fields
            const summaryField = document.getElementById('npc-summary');
            const infoField = document.getElementById('npc-info');
            if (summaryField) {
                tribute.attach(summaryField);
            }
            if (infoField) {
                tribute.attach(infoField);
            }

            // Attach Tribute.js to comment or other fields as necessary
            const commentInput = document.getElementById('npc-comment');
            if (commentInput) {
                tribute.attach(commentInput);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Function to load NPC data dynamically into the viewer
function loadNPCData(npcId) {
    
    console.log(npcId)
    fetch(`/npc/${npcId}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById('npc-viewer').innerHTML = data;  // Load HTML into viewer
            
            initializeTagifyAndTribute();
            
             // Handle Tagify data for tags, talents, and traits (from the rendered HTML)
             const tags = document.querySelector('#npc-tags')?.textContent || '';
             const talents = document.querySelector('#npc-talents')?.textContent || '';
             const traits = document.querySelector('#npc-traits')?.textContent || '';
 
             if (window.tagifyTags) {
                 window.tagifyTags.removeAllTags();
                 if (tags) window.tagifyTags.addTags(tags.split(','));
             }
 
             if (window.tagifyTalents) {
                 window.tagifyTalents.removeAllTags();
                 if (talents) window.tagifyTalents.addTags(talents.split(','));
             }
 
             if (window.tagifyTraits) {
                 window.tagifyTraits.removeAllTags();
                 if (traits) window.tagifyTraits.addTags(traits.split(','));
             }

            // Format mentions after loading
            //formatMentions('npc-summary');
            //formatMentions('npc-info');
            
            applyPlaceholders();  // Apply placeholders to dynamically loaded content
            initializeAutoSave();
        })
        .catch(error => {
            console.error('Error fetching NPC data:', error);
        });
}

// Format mention to links DEPRECATED?
function formatMentions(id) {
    const element = document.getElementById(id);
    const mentions = element.querySelectorAll('.npc-mention');

    mentions.forEach(mention => {
        const npcId = mention.getAttribute('data-id');
        mention.setAttribute('href', 'javascript:void(0)');  // Make it a clickable link
        mention.addEventListener('click', () => {
            loadNPCData(npcId);  // Load the NPC when the link is clicked
        });
    });
}

// Add click event listener to handle opening NPC from mentions
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('npc-mention')) {
        event.preventDefault();  // Prevent the default link behavior

        const npcId = event.target.getAttribute('data-id');  // Get the NPC ID from the data-id attribute
        if (npcId) {
            loadNPCData(npcId);  // Call the same function to load the NPC
        }
    }
});

// Function to save NPC data
function saveNPC() {
    console.log("Auto-save NPC function called");

    // Function to get the content of a contenteditable element, ignoring the placeholder
    function getEditableContent(id) {
        const element = document.getElementById(id);
        const placeholder = element.getAttribute('placeholder') || '';  // Dynamically fetch the 'placeholder' attribute
        if (element.textContent.trim() === placeholder) {
            return '';  // Return empty if the placeholder is still there
        }
        return element.innerHTML.trim();  // Return innerHTML to capture HTML tags (e.g., <a>)
    }

    // Function to safely get an element's value, using getEditableContent for contenteditable fields
    function getElementValue(id) {
        const element = document.getElementById(id);
        return element ? (element.value ? element.value.trim() : getEditableContent(id)) : ''; 
    }

    // Function to extract IDs from NPC mentions using the data-id attribute in the <a> tags
    function extractMentionedNPCIds(content) {
        // Create a temporary container to parse the content
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;  // Parse the content as HTML

        // Find all elements with the class "npc-mention" and extract their data-id attributes
        const mentions = tempDiv.querySelectorAll('.npc-mention');
        let ids = [];
        mentions.forEach(mention => {
            const npcId = mention.getAttribute('data-id');
            if (npcId) {
                ids.push(npcId);  // Collect the ID
            }
        });

        console.log("Extracted NPC IDs from mentions:", ids);
        return ids;
    }

    // Collect the necessary data for saving
    const npcData = {
        id: getElementValue("npc-id"),
        name: getElementValue("npc-name"),
        description: getElementValue("npc-description"),
        summary: getElementValue("npc-summary"),
        info: getElementValue("npc-info"),
        image: getElementValue("npc-image"),
        rank: getElementValue("npc-rank"),
        title: getElementValue("npc-title"),
        trappings: getElementValue("npc-trappings"),
        skills: getElementValue("npc-skills").split(",").map(s => s.trim()).filter(s => s !== ""),
        stats: {
            M: getElementValue("npc-stats-M"),
            WS: getElementValue("npc-stats-WS"),
            BS: getElementValue("npc-stats-BS"),
            S: getElementValue("npc-stats-S"),
            T: getElementValue("npc-stats-T"),
            I: getElementValue("npc-stats-I"),
            Ag: getElementValue("npc-stats-Ag"),
            Dex: getElementValue("npc-stats-Dex"),
            Int: getElementValue("npc-stats-Int"),
            WP: getElementValue("npc-stats-WP"),
            Fel: getElementValue("npc-stats-Fel"),
            W: getElementValue("npc-stats-W")
        },
        talents: window.tagifyTalents ? window.tagifyTalents.value.map(tag => tag.value) : [],
        traits: window.tagifyTraits ? window.tagifyTraits.value.map(tag => tag.value) : [],
        tags: window.tagifyTags ? window.tagifyTags.value.map(tag => tag.value) : [],
        mentions: extractMentionedNPCIds(getElementValue("npc-summary"))
            .concat(extractMentionedNPCIds(getElementValue("npc-info")))
    };

    // Log the NPC data before sending it to the server
    console.log("Collected NPC data:", JSON.stringify(npcData, null, 2));

    // Send the NPC data to the server
    fetch('/save_npc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ npcData })
    })
    .then(response => response.json())
    .then(data => {
        console.log('NPC saved successfully:', data);
    })
    .catch(error => {
        console.error('Error saving NPC:', error);
    });
}

// Function to save new tags to tags.json
/*
function saveNewTag(tag) {
    fetch('/save_tag', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tag: tag })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Tag saved successfully:', data);
    })
    .catch(error => {
        console.error('Error saving tag:', error);
    });
}
*/

document.addEventListener('DOMContentLoaded', function() {
    const tagCloudContainer = document.getElementById('tag-cloud-container');
    let selectedTags = [];

    // Fetch tags from the backend API
    fetch('/api/tags')
        .then(response => response.json())
        .then(data => {
            const tags = data.tags;  // Get the list of tags from the response
            tags.forEach(tag => {
                // Create a button for each tag
                const tagButton = document.createElement('button');
                tagButton.classList.add('tag-button');
                tagButton.textContent = tag;
                tagButton.setAttribute('data-tag', tag.toLowerCase());

                // Add event listener for toggling the filter
                tagButton.addEventListener('click', function() {
                    const tagValue = tagButton.getAttribute('data-tag');

                    // Toggle active class
                    tagButton.classList.toggle('active');

                    // Add or remove the tag from the selectedTags array
                    if (selectedTags.includes(tagValue)) {
                        selectedTags = selectedTags.filter(t => t !== tagValue);
                    } else {
                        selectedTags.push(tagValue);
                    }

                    filterNPCsByTags(selectedTags);
                });

                // Append the button to the tag cloud container
                tagCloudContainer.appendChild(tagButton);
            });
        })
        .catch(error => console.error('Error fetching tags:', error));

    // Function to filter NPCs by selected tags
    function filterNPCsByTags(tags) {
        const npcItems = document.querySelectorAll('.npc-item');

        if (tags.length === 0) {
            // If no tags are selected, show all NPCs
            npcItems.forEach(item => item.style.display = '');
            return;
        }

        npcItems.forEach(item => {
            const npcTags = item.getAttribute('data-tags').toLowerCase();
            const matches = tags.some(tag => npcTags.includes(tag));
            if (matches) {
                item.style.display = '';  // Show item if it matches any selected tag
            } else {
                item.style.display = 'none';  // Hide item if it doesn't match
            }
        });
    }
});




let saveTimeout;
// Function to handle auto-save with debounce
function triggerAutoSave() {
    // Clear any existing timeout
    clearTimeout(saveTimeout);

    // Set a delay before triggering the save to prevent frequent saves
    saveTimeout = setTimeout(() => {
        console.log('Auto-saving NPC data...');
        saveNPC();  // Call the save function 
    }, 500);  // Adjust the delay as needed
}

function initializeAutoSave() {
    const autoSaveFields = document.querySelectorAll('input, textarea, select, [contenteditable="true"]');

    // Add blur event listener to all relevant fields
    autoSaveFields.forEach(field => {
        field.addEventListener('blur', () => {
            triggerAutoSave();
        });
    });

    // Ensure that Tagify blur events are also covered
    if (window.tagifyTalents) {
        window.tagifyTalents.on('blur', () => triggerAutoSave());
    }
    if (window.tagifyTags) {
        window.tagifyTags.on('blur', () => triggerAutoSave());
    }
    if (window.tagifyTraits) {
        window.tagifyTraits.on('blur', () => triggerAutoSave());
    }
}

function loadNewNPC() {
    // Get modal elements
    const modal = document.getElementById('npcModal');
    const closeModalBtn = document.querySelector('.modal .close');
    const npcNameInput = document.getElementById('npc-name-input');
    const createNPCBtn = document.getElementById('npc-create-btn');
    const cancelNPCBtn = document.getElementById('npc-cancel-btn');
    
    // Show the modal
    modal.style.display = 'block';

    // Close modal when clicking the close button or cancel
    closeModalBtn.onclick = function() {
        modal.style.display = 'none';
    };
    cancelNPCBtn.onclick = function() {
        modal.style.display = 'none';
    };

    // Close modal when clicking outside of the modal content
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };

    // When the user clicks "OK", create the new NPC
    createNPCBtn.onclick = function() {
        const npcName = npcNameInput.value.trim();
        
        if (npcName) {
            // Generate a new NPC ID
            const npcId = generateUniqueId();

            // Create the new NPC object with all necessary fields
            const newNPC = {
                id: npcId,
                name: npcName,
                description: "",
                summary: "",
                info: "",
                image: "unknown.png",
                title: "",
                rank: "",
                trappings: "",
                stats: {
                    M: "",
                    WS: "",
                    BS: "",
                    S: "",
                    T: "",
                    I: "",
                    Ag: "",
                    Dex: "",
                    Int: "",
                    WP: "",
                    Fel: "",
                    W: ""
                },
                skills: [],
                talents: [],
                traits: [],
                tags: [],  // Empty tags initially
                mentions: [],  // No mentions yet
                tag_ids: []  // No tag IDs yet
            };

            // Call the server to add the new NPC to the JSON file
            fetch('/npc/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newNPC)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // After successful creation, load the new NPC into the viewer
                    loadNPCData(npcId);
                } else {
                    console.error('Error creating NPC:', data.message);
                }
            })
            .catch(error => {
                console.error('Error saving new NPC:', error);
            });

            // Close the modal after creation
            modal.style.display = 'none';
            
        } else {
            alert("Please enter a name for the NPC.");
        }
    };
}

// Helper function to generate a unique ID
function generateUniqueId() {
    return 'npc-' + Math.random().toString(36).substr(2, 9);  // Simple unique ID generator
}


// Helper function to generate a unique ID
function generateUniqueId() {
    return 'npc-' + Math.random().toString(36).substr(2, 9);  // Simple unique ID generator
}

async function generateOpenAIImage() {
    try {
        const npcName = document.getElementById("npc-name").textContent.trim();  // Get NPC name
        const npcDescription = document.getElementById("npc-description").textContent.trim();  // Get NPC description
        const npcID = document.getElementById("npc-id").value.trim();
    
        if (!npcDescription) {
            alert("Please provide a valid Description to generate an image.");
            return;
        }


        // Send the prompt and NPC name to the backend to generate an image
        const response = await axios.post('/generate_image', {
            prompt: npcDescription,
            npc_name: npcName,  // Send the NPC name along with the prompt
            npc_id: npcID
        });

        console.log("Response from server:", response.data);  // Log server response


        if (response.data && response.data.imageUrl) {
            document.getElementById("npc-image").value = response.data.imageUrl;  // Update the image field with the filename
            console.log("Image generated successfully:", response.data.imageUrl);
        }
    } catch (error) {
        console.error('Error generating image:', error);
        alert('Failed to generate an image. Check the console for more details.');
    }
}


//Add placeholder text
function applyPlaceholders() {
    const editableElements = document.querySelectorAll('[placeholder]');

    editableElements.forEach(element => {
        const placeholderText = element.getAttribute('placeholder');

        // Function to check if the element is empty and add a placeholder
        function checkPlaceholder() {
            if (!element.textContent.trim()) {
                element.classList.add("placeholder");
                element.textContent = placeholderText;
            }
        }

        // Remove placeholder when focused
        element.addEventListener('focus', function() {
            if (element.classList.contains("placeholder")) {
                element.textContent = "";
                element.classList.remove("placeholder");
            }
        });

        // Reapply placeholder if content is empty on blur
        element.addEventListener('blur', function() {
            if (!element.textContent.trim()) {
                element.classList.add("placeholder");
                element.textContent = placeholderText;
            }
        });

        // Initialize placeholder on page load
        checkPlaceholder();
    });
}

