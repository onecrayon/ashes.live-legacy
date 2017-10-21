<template>
	<div class="listing-wrapper">
		<card-list v-if="isListType('list')"></card-list>
		<card-table v-if="isListType('table')"></card-table>
	</div>
</template>

<script>
	import CardList from './list.vue'
	import CardTable from './table.vue'

	export default {
		components: {
			'card-list': CardList,
			'card-table': CardTable
		},
		methods: {
			isListType (listType) {
				return this.$store.state.options.listType === listType
			}
		}
	}
</script>
