<script>
    import { Button, Dropdown, Radio } from 'flowbite-svelte';
    import DownIcon from '../icons/DownIcon.svelte';
    export let title = 'Options'
    export let options = [['option1', 'op1'], ['option2', 'op2']];
    export let value = 0;
</script>

<div class='w-full h-full'>
    <Button class='bg-amber-500 hover:bg-amber-700 w-full h-full justify-between rounded-b-none'>
        <p class='w-[45%] text-left border-r-2'>Select {title} </p> <p class='flex items-center font-bold w-[45%] text-ellipsis'> current: {options[value][0]}</p> 
        <DownIcon sx='m-0 text-white'/>
    </Button>
    <Dropdown class="p-3 space-y-3 text-sm">
        {#each options as option, i}
            <Radio class='p-1 rounded hover:bg-amber-200' name={`option${option[0]}`} bind:group={value} value={i}>
                {option[0]}
            </Radio>
        {/each}
    </Dropdown>
</div>