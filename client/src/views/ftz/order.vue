<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">加课</el-button>
        <el-input
          v-model="listQuery.user"
          placeholder="输入用户id"
          style="width: 300px"
          class="filter-item"
          @keyup.native="handleFilter"
        />
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="resetFilter"
        >查询
        </el-button
        >
      </div>
    </el-card>

    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.results.filter(
          (data) =>
            !search || data.title.toLowerCase().includes(search.toLowerCase())
        )
      "
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100"
      stripe
      border
      v-el-height-adaptive-table="{ bottomOffset: 50 }"
    >
      <el-table-column label="订单id" width="80">
        <template slot-scope="scope">{{ scope.row.id }}</template>
      </el-table-column>
      <el-table-column label="用户id">
        <template slot-scope="scope">{{ scope.row.user }}</template>
      </el-table-column>
      <el-table-column label="商品id">
        <template slot-scope="scope">{{ scope.row.product }}</template>
      </el-table-column>
      <el-table-column label="订单金额">
        <template slot-scope="scope">{{ scope.row.total_amount }}</template>
      </el-table-column>
      <el-table-column label="订单状态">
        <template slot-scope="scope">{{ scope.row.status }}</template>
      </el-table-column>
      <el-table-column label="创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.create_time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间">
        <template slot-scope="scope">
          <span>{{ scope.row.update_time }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="mini"
            icon="el-icon-edit"
            :disabled="!checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="mini"
            icon="el-icon-delete"
            :disabled="!checkPermission(['position_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-show="tableDataList.count>0"
      :total="tableDataList.count"
      :page-size.sync="listQuery.page_size"
      :current-page.sync="listQuery.page"
      @current-change="getList"
    ></el-pagination>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑产品' : '新增商品'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="80px"
        label-position="right"
      >
        <el-form-item label="用户id" prop="user">
          <el-input v-model="tableData.id" placeholder="用户id"/>
        </el-form-item>
        <el-form-item label="商品id" prop="product">
          <el-input v-model="tableData.product" placeholder="商品id"/>
        </el-form-item>
        <el-form-item label="订单金额(元)" prop="total_amount">
          <el-input v-model="tableData.total_amount" placeholder="商品价格，支持小数点后两位"/>
        </el-form-item>
        <el-form-item label="订单状态" prop="status">
          <el-input v-model="tableData.status" placeholder="状态"/>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getCourseList,
} from "@/api/course";
import {
  getOrderById,
  getOrderList,
  createOrder,
  updateOrder,
  deleteOrder
} from "@/api/order";
import {genTree} from "@/utils";
import checkPermission from "@/utils/permission";

const defaultM = {};
export default {
  data() {
    return {
      tableData: {
        id: "",
        total_amount: "",
        status: "",
        user: "",
        product: "",
        create_time: "",
        update_time: ""
      },
      search: "",
      tableDataList: {},
      courseScList:[],
      statusOptions: {},
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      courseList: [],
      course: null,
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {
        module: 'product',
        service: 'type'
      }
    };
  },
  computed: {},
  created() {
    this.getList();
    // this.getProductTypeList();
    // this.getProductStatusList();
    // this.getCourseList().then(() => {
    //   this.getList();
    // });

  },
  methods: {
    checkPermission,
    getList() {
      this.listLoading = true;
      this.listQuery.course = this.course;
      getOrderList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.listQuery.search ||
          data.title.toLowerCase().includes(this.listQuery.search.toLowerCase())
      );
      this.tableData = genTree(newData);
    },
    handleAdd() {
        this.tableData = Object.assign({}, defaultM);
        this.dialogType = "new";
        this.dialogVisible = true;
        this.tableData.survey = this.course;
        this.$nextTick(() => {
            this.$refs["Form"].clearValidate();
        });
    },
    handleEdit(scope) {
        this.tableData = Object.assign({}, scope.row); // copy obj
        this.dialogType = "edit";
        this.dialogVisible = true;
        this.$nextTick(() => {
            this.$refs["Form"].clearValidate();
        });
    },
    handleDelete(scope) {
        this.$confirm("确认删除?", "警告", {
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            type: "error",
        }).then(async () => {
            await deleteOrder(scope.row.id);
            this.getList();
            this.$message({
                type: "success",
                message: "成功删除!",
            });
        }).catch((err) => {
            console.error(err);
        });
    },
    goToQuestionsPage(scope) {
        this.$router.push({name: 'questions', params: scope});
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateOrder(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createOrder(this.tableData).then((res) => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "新增成功",
                type: "success",
              });
            });
          }
        } else {
          return false;
        }
      });
    },
  },
};
</script>
