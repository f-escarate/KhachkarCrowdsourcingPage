<script>
    import { onMount } from 'svelte';
    import data from '$lib/home.json';
    import { base } from "$app/paths";
    const tutorial_styles = [
        "animate-delay-100 bg-amber-500",
        "animate-delay-300 bg-yellow-400",
        "animate-delay-500 bg-green-500"
    ];

    const text_style = (idx) => {
        let margins = ['md:mt-[-2%]', 'md:mb-[-2%]'];
        let md_style = `md:w-2/3 lg:w-[60%] xl:w-[52%] md:text-xl z-10 ${margins[idx%2]}`; 
        let sm_style = 'w-full'
        return `h-full p-5 text-xl border-4 border-amber-500 bg-amber-300 text-black whitespace-pre-line ${md_style} ${sm_style}`;
    }
    const div_style = (idx) => {
        let paddings = ['pb-[2%]', 'pt-[2%]'];
        let directions = ['flex-row', 'flex-row-reverse']
        return `animated-div opacity-0 flex w-full md:my-10 relative h-full ${paddings[idx%2]} ${directions[idx%2]}`;
    }
    const img_style = (idx) => {
        let positions = ['right-0', 'left-0'];
        return `max-w-[60%] lg:min-w-[52%] h-full bottom-0 object-cover absolute invisible md:visible ${positions[idx%2]}`
    }
    function addAnimationStyles(targets, styles) {
        const options = {
            root: null, // use the viewport as the root
            rootMargin: '0px',
            threshold: 0.5, // change this value as needed, 0.5 means when 50% of the element is visible
        };
        for (let i = 0; i < targets.length; i++){
            let target = targets[i];
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        for (let style of styles)
                            entry.target.classList.add(style);
                        observer.unobserve(entry.target);
                    }
                });
            }, options);

            if (target) 
                observer.observe(target);
        }
    }

    onMount(() => {
        const targets = document.querySelectorAll('.animated-div');
        const cards = document.querySelectorAll('.animated-card');

        const div_anim_styles = ['animate-fade-right', 'animate-duration-500', 'animate-ease-out']
        const div_card_styles = ['animate-fade-left', 'animate-duration-300', 'animate-ease-out']
        addAnimationStyles(targets, div_anim_styles);
        addAnimationStyles(cards, div_card_styles);
    });
</script>

<div class='flex flex-col h-full relative md:mx-10'>
    {#each data.divs_data as element, i}
        <div class={div_style(i)}>
            <div class={text_style(i)}>
                {element.text}
            </div>
            <img
                class={img_style(i)}
                src={`${base}${element.photo}`}
                alt={`${base}${element.photo}`}
            />
        </div>
    {/each}
    <div class='flex flex-col lg:flex-row mx-2 my-5 gap-4'>
        {#each data.cards_data as element, i}
            <div class={'animated-card opacity-0 w-full min-h-full p-10 text-white '+tutorial_styles[i]}>
                <h1 class='text-4xl font-bold mb-8'>{element.name}</h1>
                {#each Object.entries(element.sections) as [title, text]}
                    <div class='my-3'>
                        <p class='font-bold text-lg'>{title}</p>
                        <p>{text}</p>
                    </div>
                {/each}
            </div>
        {/each}
    </div>
</div>