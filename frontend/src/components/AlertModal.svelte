<script>
    import { Modal, Button } from 'flowbite-svelte';
    import CloseIcon from './icons/CloseIcon.svelte';
    export let title = '';
    export let message = '';
    export let show = false;
    export let isConfirm = false;
    let fontColor = 'text-green-500';
    export let handleYesButton = () => {
        show = false;
    }
    export let handleNoButton = () => {
        show = false;
    }
    export let handleOkButton = () => {
        show = false;
    }
    export const prepareAlert = (t, m, good, ok_action=()=>{}) => {
        title = t;
        message = m;
        isConfirm = false;
        fontColor = good ? 'text-green-500' : 'text-red-500';
        handleOkButton = ()=>{ok_action(); show=false};
        show = true;
    }
    export const prepareConfirmation = (t, m, yes_action, no_action, good) => {
        title = t;
        message = m;
        isConfirm = true;
        fontColor = good ? 'text-green-500' : 'text-red-500';
        handleYesButton = ()=>{yes_action(); show=false};
        handleNoButton = ()=>{ no_action(); show=false;};
        show = true;
    }
</script>

<Modal bind:open={show} title={title} class={fontColor}>
    <p class='font-semibold'>{message}</p>
    <svelte:fragment slot="footer">
        {#if isConfirm}
            <Button class='bg-red-500 hover:bg-red-700' on:click={e => handleNoButton()}>
                <CloseIcon sx='m-0 mr-1 text-white'/>
                No
            </Button>
            <Button class="bg-cyan-500 hover:bg-cyan-700" on:click={e => handleYesButton()}>
                Yes
            </Button>
        {:else}
            <Button class='bg-amber-500 hover:bg-amber-700' on:click={e => handleOkButton()}>
                <CloseIcon sx='m-0 mr-1 text-white'/>
                Ok
            </Button>
        {/if}
    </svelte:fragment>
</Modal>