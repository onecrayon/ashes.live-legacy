<template>
	<modal :show="show" @close="close">
		<h2>Confirm deletion</h2>

		<p><strong>Deleting a deck is permanent!</strong> Are you sure you want to delete this deck?</p>

		<div class="text-right">
			<button class="btn" @click="close">Cancel</button>
			<button class="btn btn-danger" @click="confirmDelete"><i class="fa fa-trash"></i> Delete it!</button>
		</div>
	</modal>
</template>

<script>
	import qwest from 'qwest'
	import Modal from 'app/components/modal.vue'

	export default {
		components: {
			'modal': Modal
		},
		props: ['show'],
		methods: {
			close () {
				this.$emit('close')
			},
			confirmDelete () {
				qwest.delete('/api/decks/' + this.$store.state.deck.id).then(() => {
					window.location.href = '/decks/mine/'
				})
			}
		}
	}
</script>

