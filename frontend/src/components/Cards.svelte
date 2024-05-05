<script>
    import { base } from "$app/paths";
    import { onMount } from "svelte";
    import { addAnimationStyles } from "$lib/utils";
    export var cards_data;
    export const tutorial_styles = [
        "animate-delay-100 bg-amber-400",
        "animate-delay-300 bg-amber-500",
        "animate-delay-500 bg-amber-600"
    ];
    onMount(() => {
        const cards = document.querySelectorAll('.animated-card');
        const div_card_styles = ['animate-fade-left', 'animate-duration-300', 'animate-ease-out']
        addAnimationStyles(cards, div_card_styles);
    });
</script>

<div class='flex flex-col lg:flex-row my-5 gap-4'>
    {#each cards_data as element, i}
        <div class={'animated-card opacity-0 flex flex-col w-full min-h-full p-7 text-white '+tutorial_styles[i]}>
            <h1 class='text-3xl font-bold'>{element.title}</h1>
            <h2 class='text-2xl font-semibold mb-8'>{element.subtitle}</h2>
            {#if element.sections}
                {#each Object.entries(element.sections) as [title, text]}
                    <div class='my-3'>
                        <p class='font-bold text-lg'>{title}</p>
                        <p>{text}</p>
                    </div>
                {/each}
            {/if}
            {#if element.image}
                <img
                    class='h-full object-cover'
                    src={`${base}${element.image}`}
                    alt={`${base}${element.image}`}
                />
            {/if}
        </div>
    {/each}
</div>