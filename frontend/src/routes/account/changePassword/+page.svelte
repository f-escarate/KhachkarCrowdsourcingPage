<script>
    import { HOST } from '$lib/constants';
    import { Button, FloatingLabelInput } from 'flowbite-svelte';
    import { base } from "$app/paths";
    import { auth_post_request } from '$lib/utils';
    import AlertModal from '../../../components/AlertModal.svelte';
    let alertComponent;
    let old_pass = '';
    let new_pass1 = '';
    let new_pass2 = '';
    const handleChangePass = () => {
        if (new_pass1 !== new_pass2) {
            alertComponent.prepareAlert('Passwords do not match', 'The new passwords do not match', false);
            return;
        }
        let data = new FormData();
        data.append('old_pass', old_pass);
        data.append('new_pass', new_pass1);
        auth_post_request(`${HOST}/change_password/`, data, 'PATCH')
        .then(response => response.json())
        .then(json => {
            if (json.status == 'success') {
                alertComponent.prepareAlert(
                    'Password changed', 'Your password has been changed successfully', true,
                    () => window.location.href = `${base}/account/`);
            } else {
                alertComponent.prepareAlert('Failed to change password', json.msg, false);
            }
        });
    
    }
    const handleEnter = (e) => {
        if (e.key === 'Enter') handleChangePass();
    }
</script>

<AlertModal bind:this={alertComponent}/>

<div class='mx-auto my-4 md:w-1/2 flex flex-col gap-4'>
    <h1 class='text-4xl font-bold'>Change password</h1>
    <FloatingLabelInput style="filled" name="old_pass" id="old_pass" type="text" label="Old password" bind:value={old_pass}/>
    <FloatingLabelInput style="filled" name="new_pass1" id="new_pass1" type="text" label="New password" bind:value={new_pass1}/>
    <FloatingLabelInput style="filled" name="new_pass2" id="new_pass2" type="text" label="Repeat the (new) password" bind:value={new_pass2} on:keydown={handleEnter}/>
    <Button class='w-1/2 mx-auto' on:click={handleChangePass}>Change password</Button>
</div>