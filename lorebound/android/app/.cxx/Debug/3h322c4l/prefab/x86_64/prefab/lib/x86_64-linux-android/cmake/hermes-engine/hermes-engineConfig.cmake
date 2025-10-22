if(NOT TARGET hermes-engine::libhermes)
add_library(hermes-engine::libhermes SHARED IMPORTED)
set_target_properties(hermes-engine::libhermes PROPERTIES
    IMPORTED_LOCATION "C:/Users/Labadmin/.gradle/caches/8.13/transforms/d0ba07c8fdf88f48a7f363e3b05c45f7/transformed/hermes-android-0.81.4-debug/prefab/modules/libhermes/libs/android.x86_64/libhermes.so"
    INTERFACE_INCLUDE_DIRECTORIES "C:/Users/Labadmin/.gradle/caches/8.13/transforms/d0ba07c8fdf88f48a7f363e3b05c45f7/transformed/hermes-android-0.81.4-debug/prefab/modules/libhermes/include"
    INTERFACE_LINK_LIBRARIES ""
)
endif()

