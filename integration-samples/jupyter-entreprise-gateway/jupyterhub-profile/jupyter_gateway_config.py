from kubespawner import KubeSpawner
import uuid

JUPYTER_GATEWAY_URL             = "jupyter_gateway_url"
JUPYTER_GATEWAY_API_TOKEN       = "gw_api_token"
SPARK_DRIVER_IMAGE_OPTION       = "spark_driver_image"
SPARK_DRIVER_MEMORY_MB_OPTION   = "driver_memory_md"
SPARK_DRIVER_CPU_REQUEST_OPTION = "driver_cpu_request"

class JupyterGatewayProfileKubeSpawner(KubeSpawner):
    """A KubeSpawner subclass that launches notebook kernels on the
    Jupyter Entreprise Gateway rather than on a Jupyter server pod when jupyter_gateway_url is provided
    """

    async def load_user_options(self):
        await super().load_user_options()

    async def options_from_form(self, form_data):
        options = super()._options_from_form(form_data)
        selected_slug = options["profile"]
        selected_profile = None
        for profile in self.profile_list:
            if "slug" in profile and profile["slug"] == selected_slug:
                selected_profile = profile
                break

        if selected_profile and "kubespawner_override" in selected_profile \
            and JUPYTER_GATEWAY_URL in selected_profile["kubespawner_override"]:
            options[JUPYTER_GATEWAY_URL]             = selected_profile["kubespawner_override"][JUPYTER_GATEWAY_URL]
            options[JUPYTER_GATEWAY_API_TOKEN]       = form_data[f"gw-api-token-{selected_slug}"][0]
            options[SPARK_DRIVER_IMAGE_OPTION]       = form_data[f"profile-option-{selected_slug}--image"][0]
            options[SPARK_DRIVER_MEMORY_MB_OPTION]   = form_data[f"driver-memory-{selected_slug}"][0]
            options[SPARK_DRIVER_CPU_REQUEST_OPTION] = form_data[f"driver-cpu-request-{selected_slug}"][0]
        else:
            self.log.info(f"Running with JupyterHub single-user server")
        

        return options

    def get_args(self):
        """Start the jupyterhub single user with JEG arguments"""

        args = super().get_args()
        if JUPYTER_GATEWAY_URL in self.user_options:
            jupyter_gateway_url = self.user_options[JUPYTER_GATEWAY_URL]
            gw_api_token = self.user_options[JUPYTER_GATEWAY_API_TOKEN]
            args.extend([
                f"--gateway-url={jupyter_gateway_url}",
                "--GatewayWebSocketConnection.kernel_ws_protocol=",
                "--GatewayClient.request_timeout=600",
                f"--GatewayClient.auth_token={gw_api_token}",
            ])
        return args

    def get_env(self):
        """Flow current user from JupyterHub to Jupyter Gateway"""

        env = super().get_env()
        if JUPYTER_GATEWAY_URL in self.user_options:
            env['KERNEL_USERNAME'] =  self.user.name
            # Spark Submit options
            driver_memory_mb = self.user_options[SPARK_DRIVER_MEMORY_MB_OPTION]
            driver_cpu_request = self.user_options[SPARK_DRIVER_CPU_REQUEST_OPTION]
            driver_image = self.user_options[SPARK_DRIVER_IMAGE_OPTION]
            # Executor options (image, memory, cpu, etc) can be customized with the notebook code
            env['KERNEL_EXTRA_SPARK_OPTS'] = ' '.join([f"--conf spark.driver.memory={driver_memory_mb}m",
                                                       f"--conf spark.kubernetes.driver.request.cores={driver_cpu_request}"
                                                      ]
                                                      )
            # Spark driver image
            env['KERNEL_IMAGE'] = driver_image

            self.log.info(f"Running Spark image '{driver_image}' with Jupyter Gateway '{self.user_options[JUPYTER_GATEWAY_URL]}' \
                          using spark submit options: {env['KERNEL_EXTRA_SPARK_OPTS']}")

        return env

c.JupyterHub.spawner_class = JupyterGatewayProfileKubeSpawner
# Timeout (in seconds) before giving up on starting of single-user server.
c.KubeSpawner.start_timeout = 500
#c.Authenticator.enable_auth_state = True
c.KubeSpawner.additional_profile_form_template_paths = ["/usr/local/etc/jupyterhub/templates/jupyter_gateway/"]
