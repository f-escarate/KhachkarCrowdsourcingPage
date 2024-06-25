<script>
    import { auth_get_json } from '../../lib/utils.js';
    import { base } from "$app/paths.js";
    import { HOST } from '$lib/constants.js';
    import { onMount } from 'svelte';
    let status = 'loading...'
    let last_restarted = 'Unknown';
    let last_stopped = 'Unknown';
    let gpu = 'Unknown';
    let status_color = 'text-yellow-500';
    onMount(async () => {
        const response = await auth_get_json(`${HOST}/get_server_status`);
        let response_json = await response.json();
        if (response_json.status == 'error') {
            alert(response_json.msg);
            window.location.href = `${base}`;
            return;
        } else if (response_json.status == 'valdi_error') {
            status = response_json.msg;
        } else if (response_json.status == 'success') {
            status = response_json.msg.server_status;
            if (status == 'running') {
                status_color = 'text-green-500';
            } else if (status == 'stopped'){
                status_color = 'text-red-500';
            }
            last_restarted = response_json.msg.last_restarted.split("T");
            last_stopped = response_json.msg.last_stopped.split("T");
            last_restarted[1] = last_restarted[1].split(".")[0];
            last_stopped[1] = last_stopped[1].split(".")[0];
            last_restarted = last_restarted.join(" | ");
            last_stopped = last_stopped.join(" | ");
            gpu = response_json.msg.gpu;
        }
        
    });
</script>


<h1 class='text-4xl font-bold'>Check server status</h1>
<div class='grid gap-2 grid-cols-2 max-w-[500px] p-2 rounded-xl bg-amber-100'>
    <b>Server status</b>
    <p class={status_color}>{status}</p>
    <b>Last restarted time</b>
    <p>{last_restarted}</p>
    <b>Last stopped time</b>
    <p>{last_stopped}</p>
    <b>GPU Model</b>
    <p>{gpu}</p>
</div>
