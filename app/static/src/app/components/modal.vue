<template>
	<transition name="modal">
		<div class="modal-mask" @click="close" v-show="show">
			<div class="modal-container" @click.stop>
				<div class="modal-body">
					<slot></slot>
				</div>
				<div class="modal-footer">
					<slot name="footer"></slot>
				</div>
			</div>
		</div>
	</transition>
</template>

<script>
	export default {
		template: '#modal-template',
		props: ['show'],
		methods: {
			close () {
				this.$emit('close')
			},
			escapeClose (event) {
				if (this.show && event.keyCode === 27) {
					this.close()
				}
			}
		},
		mounted () {
			this.escapeCloseHandler = this.escapeClose.bind(this)
			document.addEventListener('keydown', this.escapeCloseHandler)
		},
		beforeDestroy () {
			document.removeEventListener('keydown', this.escapeCloseHandler)
		}
	}
</script>

