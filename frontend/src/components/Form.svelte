<script>
    import { FloatingLabelInput, Textarea, Label, Button } from 'flowbite-svelte';
    import { HOST } from '$lib/constants';

    export let token;
    export let http_method = 'POST';
    export let endpoint_url = '/post_khachkar/';
    export let entry = {
        title : '',
        description : '',
        location: '',
        latLong: '',
        scenario: '',
        setting: '',
        landscape: '',
        accessibility: '',
        masters_name: '',
        category: '',
        production_period: '',
        motive: '',
        condition_of_preservation: '',
        inscription: '',
        important_features: '',
        backside: '',
        history_ownership: '',
        commemorative_activities: '',
        references: '',
        date : null,
        image : null,
    };
    export const previewImage = () => {
        console.log(entry.image);
        var preview = document.getElementById('preview');
        preview.src = URL.createObjectURL(entry.image);
        preview.onload = () => {
            URL.revokeObjectURL(preview.src) // free memory
        }
    }

    const restartForm = () => {
        entry.title = '';
        entry.description = '';
        entry.location = '';
        entry.latLong = '';
        entry.scenario = '';
        entry.setting = '';
        entry.landscape = '';
        entry.accessibility = '';
        entry.masters_name = '';
        entry.category = '';
        entry.production_period = '';
        entry.motive = '';
        entry.condition_of_preservation = '';
        entry.inscription = '';
        entry.important_features = '';
        entry.backside = '';
        entry.history_ownership = '';
        entry.commemorative_activities = '';
        entry.references = '';
        entry.date = null;
        entry.image = null;
        var preview = document.getElementById('preview');
        preview.src = '';
    }

    const validation = () => {
        let msg = '';
        if (entry.title == '')
            msg += 'Title cannot be empty\n';
        if (entry.description == '')
            msg += 'Description cannot be empty\n';
        if (entry.date == null)
            msg +=  'Date cannot be empty\n';
        if (entry.image == null)
            msg += 'Image cannot be empty\n';
        
        if (msg !== '') {
            alert(msg);
            return false;
        }
        return true;
    }
    
    const handleSubmit = async (e) => {
        if (!validation()) {
            return;
        }
		const data = new FormData();
        for ( var key in entry ) {
            data.append(key, entry[key]);
        }
        const response = await fetch(`${HOST}${endpoint_url}`, {
            method: http_method,
            headers: {
                Authorization: `Bearer ${token}`
            },
            body: data
        });
        const json = await response.json();
        if (json.status == 'success') {
            alert('Successfully added');
            restartForm();
        } else {
            alert('Failed to add');
        }
    }
    const loadFile = (event) => {
        entry.image = event.target.files[0];
        previewImage();
    };

</script>
<div class='border-4 border-amber-300 p-5'>
    <div class='grid gap-6 items-end w-full md:grid-cols-2'>
        <div class='md:col-span-2'>
            <Label for="title" class="mb-2">Title</Label>
            <FloatingLabelInput style="filled" name="title" id="title" type="text" label="Title" bind:value={entry.title}/>
        </div>
        <div class='md:col-span-1 h-full flex flex-col justify-between'>
            <div class="flex flex-col gap-1">
                <FloatingLabelInput style="filled" name="location" id="location" type="text" label="Location" bind:value={entry.location}/>
                <FloatingLabelInput style="filled" name="latLong" id="latLong" type="text" label="Latitude Longitude" bind:value={entry.latLong}/>
                <FloatingLabelInput style="filled" name="scenario" id="scenario" type="text" label="Scenario" bind:value={entry.scenario}/>
                <FloatingLabelInput style="filled" name="setting" id="setting" type="text" label="Setting" bind:value={entry.setting}/>
                <FloatingLabelInput style="filled" name="landscape" id="landscape" type="text" label="Landscape" bind:value={entry.landscape}/>
                <FloatingLabelInput style="filled" name="accessibility" id="accessibility" type="text" label="Accessibility" bind:value={entry.accessibility}/>
                <FloatingLabelInput style="filled" name="masters_name" id="masters_name" type="text" label="Master's name" bind:value={entry.masters_name}/>
                <FloatingLabelInput style="filled" name="category" id="category" type="text" label="Category" bind:value={entry.category}/>
                <FloatingLabelInput style="filled" name="production_period" id="production_period" type="text" label="Production Period" bind:value={entry.production_period}/>
                <FloatingLabelInput style="filled" name="motive" id="motive" type="text" label="Motive" bind:value={entry.motive}/>
                <FloatingLabelInput style="filled" name="condition_of_preservation" id="condition_of_preservation" type="text" label="Condition of Preservation" bind:value={entry.condition_of_preservation}/>
                <FloatingLabelInput style="filled" name="inscription" id="inscription" type="text" label="Inscription" bind:value={entry.inscription}/>
                <FloatingLabelInput style="filled" name="important_features" id="important_features" type="text" label="Important features" bind:value={entry.important_features}/>
                <FloatingLabelInput style="filled" name="backside" id="backside" type="text" label="Backside" bind:value={entry.backside}/>
                <FloatingLabelInput style="filled" name="history_ownership" id="history_ownership" type="text" label="History ownership" bind:value={entry.history_ownership}/>
                <FloatingLabelInput style="filled" name="commemorative_activities" id="commemorative_activities" type="text" label="Commemorative Activities" bind:value={entry.commemorative_activities}/>
                <FloatingLabelInput style="filled" name="references" id="references" type="text" label="References" bind:value={entry.references}/>

                <Label for="date" class="mb-1">Date</Label>
                <input type="date" id="date" name="date" class="p-2" bind:value={entry.date}>
            </div>
        </div>

        <div class="h-full">
            <Label for="description" class="mb-2">Description</Label>
            <Textarea class="h-full" id="description" placeholder="Enter description" rows="5" name="description" bind:value={entry.description}/>
        </div>

        <div class="my-2 flex-row align-center">
            <Label for="image" class="mb-2">
            Upload image
            <div class="my-4 p-1 flex bg-amber-300 hover:bg-amber-500 text-center hover:text-white transition-colors duration-400 ease-in-out">
                <img id="preview" class="md:w-1/2 m-auto p-2" alt="Data">
                <input type="file" id="image" name="image" class="w-0 invisible" on:change={loadFile}>
            </div>
            </Label>
        </div>
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500' on:click={handleSubmit} pill>Add</Button>
    </div>
</div>