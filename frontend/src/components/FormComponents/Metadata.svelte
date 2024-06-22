<script>
    import { FloatingLabelInput } from 'flowbite-svelte';
    import { HOST, TEXT_FIELDS_NAMES, NUM_FIELDS_NAMES, OPTION_FIELDS_NAMES } from '$lib/constants';
    import SelectOptions from './SelectOptions.svelte';
    import { onMount } from 'svelte';
    import { auth_get_json } from '$lib/utils'
    import Cookies from 'js-cookie';
    
    export let entry;
    export let OPTION_FIELDS_OPTIONS_NAMES = {};
    export let OPTION_FIELDS_OPTIONS_IDS = {};
    onMount(async () => {
        async function get_options_list() {
            const response = await auth_get_json(`${HOST}/get_options_list/`);
            if (response.status != 200){
                alert('Failed to get options list, status code: ' + response.status);
                return;
            }
            let ret = await response.json();
            return ret;
        }

        let response = await get_options_list();
        if (response.status === 'error') {
            alert('Failed to get options list: ' + response.msg);
        } else if (response.status === 'success') {
            for( var key in OPTION_FIELDS_NAMES ) {
                let options_list = response.msg[key];
                OPTION_FIELDS_OPTIONS_NAMES[key] = options_list.map((x) => x[0]);
                OPTION_FIELDS_OPTIONS_IDS[key] = options_list.map((x) => x[1]);
            }
        } else {
            alert('Failed to get options list (unknown reason)');
        }
    });
    const TEXT_FIELDS = Object.getOwnPropertyNames(TEXT_FIELDS_NAMES);
    const NUM_FIELDS = Object.getOwnPropertyNames(NUM_FIELDS_NAMES);
    const OPTION_FIELDS = Object.getOwnPropertyNames(OPTION_FIELDS_NAMES);

    export const addDataToRequest = (req_form_data, entry) => {
        // Validate the data
        if (entry.height < 0.1) {
            alert('Height must be greater than 0.1 meters');
            return false;
        }
        // Add the data to the request
        for ( var field_name in OPTION_FIELDS_NAMES ) {
            let options_list = OPTION_FIELDS_OPTIONS_IDS[field_name];
            let option_index = entry[field_name];
            req_form_data.append(field_name, options_list[option_index]);
        }
        for ( var key in TEXT_FIELDS_NAMES ) {
            if (entry[key] !== null)
            req_form_data.append(key, entry[key]);
        }
        req_form_data.append('latitude', entry.latitude);
        req_form_data.append('longitude', entry.longitude);
        req_form_data.append('height', entry.height);
        return true;
    }

</script>

<h2 class='md:col-span-2 text-2xl font-semibold'>Metadata</h2>
{#each OPTION_FIELDS as key}
    <SelectOptions title={OPTION_FIELDS_NAMES[key]} options={OPTION_FIELDS_OPTIONS_NAMES[key]} bind:value={entry[key]}/>
{/each}
{#each NUM_FIELDS as key}
    <FloatingLabelInput style="filled" type="number" name={key} id={key} label={NUM_FIELDS_NAMES[key]} bind:value={entry[key]}/>
{/each}
{#each TEXT_FIELDS as key}
    <FloatingLabelInput style="filled" type="text" name={key} id={key} label={TEXT_FIELDS_NAMES[key]} bind:value={entry[key]}/>
{/each}