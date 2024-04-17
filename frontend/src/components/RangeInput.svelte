<script>
    import { createEventDispatcher } from "svelte";
    export let property;
    export let axis;
    export let interval;
    export let step;
    let value = interval[1];
    let name = `${property}_${axis}`;

    let dispatch = createEventDispatcher();
    const handleChange = (e) => {
        value = e.target.value;
        console.log(property, axis, value)
        dispatch('change', {
            property, axis, value
        })
    }
</script>

<div class='flex gap-4 w-full'>
    <label for={`${name}_range_input`}>{axis}</label>
    <input 
        class='w-full'
        type="range"
        id={name}
        name={`${name}_range_input`}
        min={interval[0]}
        max={interval[2]}
        value={value}
        step={step}
        on:input={handleChange}
    />
    <input
        class='max-w-24 w-24'
        type="number"
        id={`${name}_number_input`}
        name={name}
        min={interval[0]}
        max={interval[2]}
        value={value}
        step={step}
        on:input={handleChange}
    />
    <label class='hidden' for={`${name}_number_input`}>{axis}</label>   
</div>