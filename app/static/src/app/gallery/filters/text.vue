<template>
	<div class="input-group">
		<div class="form-field">
			<input v-model="search" type="text" placeholder="Filter by name or text...">
		</div>
		<button @click="clearSearch" :disabled="!search" class="btn" title="Clear Search"><i class="fa fa-times"></i></button>
	</div>
</template>

<script>
	import {debounce} from 'lodash'

	export default {
		computed: {
			search: {
				get () {
					return this.$store.state.options.search
				},
				set: debounce(function (value) {
					let search = value || null
					this.$store.commit('setSearch', search)
					this.$store.commit('filterCards')
				}, 400)
			}
		},
		methods: {
			clearSearch () {
				this.search = null
			}
		}
	}
</script>

