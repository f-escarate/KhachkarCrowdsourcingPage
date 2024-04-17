<script>
    import { createEventDispatcher } from "svelte";
    export let label;
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

<input 
    type="range"
    id={name}
    name={name}
    min={interval[0]}
    max={interval[2]}
    value={interval[1]}
    step={step}
    on:input={handleChange}
/>
<label for="pos_x">{label} {axis}: {value}</label>