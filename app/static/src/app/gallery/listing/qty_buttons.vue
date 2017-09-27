<template>
	<div class="btn-group">
		<button class="btn btn-qty"
			:class="[isQtyActive(card.id, 0) ? 'active' : '', classes]"
			@click="setCardQty(card.id, 0)" v-html="zeroOutput || 0"></button
		><button class="btn btn-qty"
			:class="[isQtyActive(card.id, 1) ? 'active' : '', classes]"
			@click="setCardQty(card.id, 1)">1</button
		><button class="btn btn-qty"
			:class="[isQtyActive(card.id, 2) ? 'active' : '', classes]"
			@click="setCardQty(card.id, 2)">2</button
		><button class="btn btn-qty"
			:class="[isQtyActive(card.id, 3) ? 'active' : '', classes]"
			@click="setCardQty(card.id, 3)">3</button>
	</div>
</template>

<script>
	export default {
		props: ['card', 'classes', 'zeroOutput'],
		methods: {
			setCardQty (id, qty) {
				this.$store.commit('setCardQty', {id: id, qty: qty})
			},
			isQtyActive (id, qty) {
				return (!this.$store.state.deck.cards[id] && qty == 0)
					|| this.$store.state.deck.cards[id] == qty
			}
		}
	}
</script>

