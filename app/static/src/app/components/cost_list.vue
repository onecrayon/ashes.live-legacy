<template>
	<span>
		<ol v-if="costs" class="costs">
			<li v-for="cost of costs" class="cost">
				<span v-if="isArray(cost)" class="parallel-costs">
					<span v-for="splitCost of cost"
						class="cost"
						:class="{highlight: isPowerCost(splitCost)}">
						<card-codes :content="splitCost"></card-codes>
					</span>
				</span>
				<card-codes v-else :content="cost" :class="{highlight: isPowerCost(cost)}"></card-codes>
			</li>
		</ol>
		<span v-else class="muted">--</span>
	</span>
</template>

<script>
	import {isArray} from 'lodash'
	import CardCodes from 'app/components/card_codes.vue'
	
	export default {
		props: {
			costs: Array,
			useHighlights: Boolean
		},
		components: {
			'card-codes': CardCodes,
		},
		methods: {
			isArray,
			isPowerCost (formattedCost) {
				if (!this.useHighlights) return false
				const firstCost = formattedCost.replace(/^.+?\[\[([a-z]+(?::[a-z]+)?)\]\].*$/i, '$1')
				const costType = firstCost.split(':')
				if (costType.length !== 2) return false
				return costType[1] === 'power'
			},
		}
	}
</script>
